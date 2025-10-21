import React, {useEffect, useMemo, useRef, useState} from 'react';

import {NotebookPanel} from '@jupyterlab/notebook';

import DisplayWidget from "./index";
import {useKernelExecutor} from "../hooks/useKernelExecutor";
import {useNotebookUpdater} from "../hooks/useNotebookUpdater";
import {getCredentials, getRegion} from "../utils/getCredentials";
import {DisplayData} from "../utils/types";
import {TelemetryEventContext, TelemetryEventType, useTelemetryJL} from '../../utils/telemetry';
import { ChartGroup, inferChartGroup } from '../utils/getChartGroup';

export interface VisualizationWidgetProps {
  data: DisplayData;
  notebookPanel: NotebookPanel;
}

export const VisualizationWidget = ({data: initData, notebookPanel}: VisualizationWidgetProps): React.ReactNode => {
  const [data, setData] = useState<DisplayData>(initData);
  const [isS3Storage, setS3Storage] = useState<boolean>(data.type === "s3");
  const [isAsyncLoading, setAsyncLoading] = useState<boolean>(false);
  const kernelExecute = useKernelExecutor(notebookPanel, data.kernel_id)
  const updateCell = useNotebookUpdater(notebookPanel);
  const { recordBIEvent } = useTelemetryJL();
  const dataRef = useRef(data);
  useEffect(() => {
    dataRef.current = data;
  }, [data]);

  const generateMetadata = useMemo(() => {
    if (kernelExecute) {
      return async () => {
        const startTime = Date.now();
        const value = await kernelExecute(`display(${data.interface_id}.generate_metadata_str())`);
        if (data.type === "cell") {
          await updateCell({...data, metadata_str: value});
        }
        recordBIEvent({
          eventType: TelemetryEventType.CLICK,
          eventContext: TelemetryEventContext.JL_CONNECTION,
          eventDetail: 'generate-metadata',
          latency: Date.now() - startTime
        });
        return value
      }
    }
  }, [data, kernelExecute, updateCell, recordBIEvent]);

  const generateSummarySchema = useMemo(() => {
    if (kernelExecute) {
      return async () => {
        const value = await kernelExecute(`display(${data.interface_id}.generate_summary_schema_str())`);
        if (data.type === "cell") {
          await updateCell({...data, summary_schema_str: value});
        }
        return value
      }
    }
  }, [data, kernelExecute, updateCell]);

  const generateColumnSchema = useMemo(() => {
    if (kernelExecute) {
      return async (column: string) => {
        const startTime = Date.now();
        const value = await kernelExecute(`display(${data.interface_id}.generate_column_schema_str(column = "${column}"))`);
        if (data.type === "cell") {
          await updateCell({...data, column_schema_str_dict: {...data.column_schema_str_dict, [column]: value}});
        }
        recordBIEvent({
          eventType: TelemetryEventType.CLICK,
          eventContext: TelemetryEventContext.JL_CONNECTION,
          eventDetail: 'generate-column-schema',
          latency: Date.now() - startTime
        });
        return value
      }
    }
  }, [data, kernelExecute, updateCell, recordBIEvent]);

  const serializeArgs = (args: Record<string, string>): string => {
    return Object.keys(args)
      .sort()
      .map(key => args[key].replace(/\|/g, '%7C'))
      .join('|');
  }

  const generatePlotData = useMemo(() => {
    if (kernelExecute) {
      return async (chartType: string, args: Record<string, string>) => {
        const startTime = Date.now();
        const chartGroup = inferChartGroup(chartType) as ChartGroup;
        const serializedArgs = serializeArgs(args);
        console.log(serializedArgs)

        // return cached value
        if (dataRef.current.type === "cell" &&
            dataRef.current.plot_data_str_dict?.[chartGroup]?.[serializedArgs]) {
          return dataRef.current.plot_data_str_dict[chartGroup][serializedArgs];
        }

        // Generate new data
        const kwargs = Object.entries(args).map(([key, value]) => `${key}="${value}"`).join(', ');
        const value = await kernelExecute(`display(${data.interface_id}
                .generate_plot_data_str("${chartType}", ${kwargs}))`);

        if (dataRef.current.type === "cell") {
          setData((prevData: DisplayData) => {
            if (prevData.type === "cell") {
              const newData = {
                ...prevData,
                plot_data_str_dict: {
                  ...prevData.plot_data_str_dict,
                  [chartGroup]: {
                    ...(prevData.plot_data_str_dict?.[chartGroup] || {}),
                    [serializedArgs]: value
                  }
                }
              };
              updateCell(newData);
              return newData;
            }
            return prevData;
          });
          recordBIEvent({
            eventType: TelemetryEventType.CLICK,
            eventContext: TelemetryEventContext.JL_CONNECTION,
            eventDetail: 'generate-plot-data',
            latency: Date.now() - startTime
          });
        }
        return value
      }
    }
  }, [kernelExecute, updateCell, recordBIEvent]);

  const updateSample = useMemo(() => {
    if (kernelExecute) {
      return async (sampleMethod: string, sampleSize: string) =>
        await kernelExecute(`display(${data.interface_id}.set_sampling_method(sample_method="${sampleMethod}", sample_size=${sampleSize}))`);
    }
  }, [data, kernelExecute]);

  useEffect(() => {
    async function updateOutput(): Promise<DisplayData | undefined> {
      if (kernelExecute) {
        await kernelExecute(`${data.interface_id}.set_storage("${isS3Storage ? "s3" : "cell"}")`);
        if (isS3Storage) {
          if (data.type != "s3") {
            const s3Path = await kernelExecute(`display(${data.interface_id}.get_s3_path())`);
            const s3Size = parseInt(await kernelExecute(`display(${data.interface_id}.get_s3_df_size())`));
            await kernelExecute(`display(${data.interface_id}.generate_metadata_str())`);
            await kernelExecute(`display(${data.interface_id}.generate_summary_schema_str())`);
            await kernelExecute(`display(${data.interface_id}.upload_dataframe_to_s3())`, 1000000).then(() => {
              setAsyncLoading(false);
            });
            return {
              type: "s3",
              kernel_id: data.kernel_id,
              interface_id: data.interface_id,
              connection_name: data.connection_name,
              original_size: data.original_size,
              s3_path: s3Path,
              s3_size: s3Size,
            }
          }
        } else {
          if (data.type != "cell") {
            // Encode the data str using base64
            const data_str = await kernelExecute(`display(${data.interface_id}.generate_sample_dataframe_str())`);
            const metadata = await kernelExecute(`display(${data.interface_id}.generate_metadata_str())`);
            const summary_schema = await kernelExecute(`display(${data.interface_id}.generate_summary_schema_str())`);
            return {
              type: "cell",
              kernel_id: data.kernel_id,
              interface_id: data.interface_id,
              connection_name: data.connection_name,
              original_size: data.original_size,
              data_str: data_str,
              metadata_str: metadata,
              summary_schema_str: summary_schema,
              column_schema_str_dict: {},
              plot_data_str_dict: {
                [ChartGroup.XY]: {},
                [ChartGroup.CATEGORY]: {},
                [ChartGroup.FINANCIAL]: {},
                [ChartGroup.CUMULATIVE]: {},
                [ChartGroup.DISTRIBUTION]: {},
                [ChartGroup.BOX]: {},
                [ChartGroup.HEATMAP]: {}
              }
            }
          }
        }
      }
      return undefined;
    }

    updateOutput().then(async displayData => {
      if (displayData) {
        setData(displayData);
        await updateCell(displayData);
      }
    }).catch(e => {
      console.error(e)
    })
  }, [isS3Storage]);

  const props = useMemo(() => {
    const props: any = {}
    if (data.type === "s3") {
      props.visualizationProps = {
        type: "s3",
        visualizationDataProps: {
          originalSize: data.original_size,
          s3Path: data.s3_path,
          s3Size: data.s3_size,
          region: getRegion(),
          credentialProvider: getCredentials(data.connection_name),
          kernelOperations: kernelExecute ? {
            updateSample: updateSample,
            generateMetadata: generateMetadata,
            generateSummarySchema: generateSummarySchema,
            generateColumnSchema: generateColumnSchema,
            generatePlotData: generatePlotData,
            setS3Storage: setS3Storage,
          } : undefined
        }
      }
    } else if (data.type === "cell") {
      props.visualizationProps = {
        type: "cell",
        visualizationDataProps: {
          originalSize: data.original_size,
          dataId: data.interface_id,
          dataStr: data.data_str,
          metadataStr: data.metadata_str,
          summarySchemaStr: data.summary_schema_str,
          columnSchemaStrDict: data.column_schema_str_dict,
          plotDataStrDict: data.plot_data_str_dict,
          kernelOperations: kernelExecute ? {
            updateSample: updateSample,
            generateMetadata: generateMetadata,
            generateSummarySchema: generateSummarySchema,
            generateColumnSchema: generateColumnSchema,
            generatePlotData: generatePlotData,
            setS3Storage: setS3Storage,
          } : undefined
        },
      }
    }
    return props;
  }, [data, kernelExecute]);

  if (data.type === "default") {
    return (<div>Preparing your data for display...</div>);
  }

  return (
    <div>
      {isAsyncLoading && (<div>Uploading data to S3...</div>)}
      <DisplayWidget
        {...props}
        key={`${data.interface_id}-${data.type}${kernelExecute ? "-withKernel" : ""}`}
        domId={data.interface_id}
      />
    </div>
  );
};
