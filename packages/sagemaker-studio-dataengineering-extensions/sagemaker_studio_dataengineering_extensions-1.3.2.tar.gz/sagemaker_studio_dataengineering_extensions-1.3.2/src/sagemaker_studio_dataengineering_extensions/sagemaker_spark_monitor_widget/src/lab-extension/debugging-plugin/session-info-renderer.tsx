import { IRenderMime } from '@jupyterlab/rendermime-interfaces';
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { ReactWidget } from '@jupyterlab/apputils';
import React from 'react';
import { getConnectionDetails } from './utils/jupyter_api_client';
import { handleEMRonEc2DebuggingLinksClicked } from './computes/emr_ec2';
import { handleEMRServerlessDebuggingLinksClicked } from './computes/emr_serverless';
import { handleGlueDebuggingLinksClicked } from './computes/glue';
import { LINK_TYPE_SPARK_UI, LINK_TYPE_DRIVER_LOG, CONNECTION_TYPE_GLUE, CONNECTION_TYPE_EMR_EC2, CONNECTION_TYPE_EMR_EKS, CONNECTION_TYPE_EMR_SERVERLESS } from './constants';
import { handleEMRonEksDebuggingLinksClicked } from './computes/emr_eks';


const SESSION_INFO_MIME_TYPE = 'application/vnd.smus.job-monitoring+json';


interface SessionInfoData {
  version: string;
  session: {
    id: string;
    connection_name: string;
    driver_logs_location: string;
    events_logs_location: string;
  };
  resource_metadata?: any;
}

interface SessionInfoTableProps {
  data: SessionInfoData;
}

const SessionInfoTable: React.FC<SessionInfoTableProps> = ({ data }) => {
  /**
   * Determines the appropriate log location based on compute type and link type.
   * - Glue: Uses events_logs_location for Spark UI, driver_logs_location for Driver Log
   * - EMR: Always uses driver_logs_location regardless of link type
   */
  const getLogLocationForCompute = (connectionDetail: any, linkType: string): string => {
    const compute = getComputeType(connectionDetail);
    if (compute == CONNECTION_TYPE_GLUE) {
      // Glue sessions support different log types
      return linkType === LINK_TYPE_SPARK_UI 
        ? data.session.events_logs_location 
        : data.session.driver_logs_location;
    } else if (compute == CONNECTION_TYPE_EMR_EC2 || compute == CONNECTION_TYPE_EMR_SERVERLESS) {
      // EMR (both EC2 and Serverless) always uses driver logs location
      return data.session.driver_logs_location;
    } else if (compute == CONNECTION_TYPE_EMR_EKS) {
      return linkType === LINK_TYPE_SPARK_UI 
        ? data.session.events_logs_location 
        : data.session.driver_logs_location;
    } else {
      console.log("Unknown Spark compute.");
      return ""
    }
  };

  const getComputeType = (connectionDetail: any) : string => {
      if (connectionDetail.props.sparkGlueProperties) {
        return CONNECTION_TYPE_GLUE
      } else if (connectionDetail.props.sparkEmrProperties) {
        // Handle EMR (EMR EC2 or EMR serverless, EMR EKS).
        const parts = connectionDetail.props.sparkEmrProperties.computeArn.split('/');
        const computeType = parts[parts.length - 2];

        if (computeType == "applications") {
          //arn:aws:emr-serverless:us-west-2:471112686700:/applications/00g0dcle2r90lf0l
          return CONNECTION_TYPE_EMR_SERVERLESS
        } else if (computeType == "virtualclusters") {
          //arn:aws:emr-containers:us-west-2:471112686700:/virtualclusters/owghrks4r2x71aq2e59tid419
          return CONNECTION_TYPE_EMR_EKS
        } else {
          //arn:aws:elasticmapreduce:us-west-2:471112686700:cluster/j-PJ3OJHC5RAFD
          return CONNECTION_TYPE_EMR_EC2
        }
      } else {
        console.log("Unknown Spark compute.");
        return ""
      }
  }

  const handleDebuggingLinkClick = async (
    applicationId: string,
    connectionName: string,
    linkType: string
  ): Promise<void> => {
    if (!applicationId) {
      console.error('Could not determine application id.');
      return;
    }

    if (!connectionName) {
      console.error('Could not determine connection name.');
      return;
    }

    try {
      const connectionDetail = await getConnectionDetails(connectionName);
      const logsLocation = getLogLocationForCompute(connectionDetail, linkType);
      const compute = getComputeType(connectionDetail);
      if (compute == CONNECTION_TYPE_GLUE) {
        await handleGlueDebuggingLinksClicked(connectionDetail, applicationId, linkType, logsLocation);
      } else if (compute == CONNECTION_TYPE_EMR_EC2) {
          await handleEMRonEc2DebuggingLinksClicked(connectionDetail, applicationId, linkType, logsLocation);
      } else if (compute == CONNECTION_TYPE_EMR_EKS) {
          await handleEMRonEksDebuggingLinksClicked(connectionDetail, linkType, logsLocation);
      } else if (compute == CONNECTION_TYPE_EMR_SERVERLESS){
          await handleEMRServerlessDebuggingLinksClicked(connectionDetail, applicationId, linkType);
      } else {
        console.log("Unknown Spark compute.");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSparkUIClick = (event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    handleDebuggingLinkClick(
      data.session.id,
      data.session.connection_name,
      LINK_TYPE_SPARK_UI
    );
  };

  const handleDriverLogClick = (event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    handleDebuggingLinkClick(
      data.session.id,
      data.session.connection_name,
      LINK_TYPE_DRIVER_LOG
    );
  };

  return (
    <table className="session_info_table">
      <tr>
        <th>Id</th>
        <th>Spark UI</th>
        <th>Driver logs</th>
      </tr>
      <tr>
        <td className="application_id">
          {data.session.id}
        </td>
        <td className="spark_ui_link">
          <a
            href=""
            target="_blank"
            {...({ log_location: "" } as any)}
            onClick={handleSparkUIClick}
          >
            link
          </a>
        </td>
        <td className="driver_log_link">
          <a
            href=""
            target="_blank"
            {...({ log_location: data.session.driver_logs_location } as any)}
            onClick={handleDriverLogClick}
          >
            link
          </a>
        </td>
      </tr>
    </table>
  );
};

class RenderedSessionInfoWidget extends ReactWidget implements IRenderMime.IRenderer {
  private _mimeType: string;
  private _data: SessionInfoData | null = null;

  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this._mimeType = options.mimeType;
    this.addClass('jp-RenderedSessionInfo');
  }

  renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    try {
      this._data = JSON.parse(model.data[this._mimeType] as string) as SessionInfoData;
      this.update();
      return Promise.resolve();
    } catch (error) {
      console.error('Error rendering session info:', error);
      return Promise.reject(error);
    }
  }

  render(): JSX.Element {
    if (!this._data) {
      return <div>Error rendering session information</div>;
    }

    return <SessionInfoTable data={this._data} />;
  }
}

export const sessionInfoMimeRender: JupyterFrontEndPlugin<void> = {
  id: 'sagemaker-session-info-mime-render',
  description: 'MIME renderer for SageMaker session info tables',
  autoStart: true,
  requires: [IRenderMimeRegistry],
  activate: (app: JupyterFrontEnd, rendermime: IRenderMimeRegistry) => {
    console.log('Session Info MIME renderer activated');
    
    rendermime.addFactory({
      safe: true,
      mimeTypes: [SESSION_INFO_MIME_TYPE],
      createRenderer: (options: IRenderMime.IRendererOptions) =>
        new RenderedSessionInfoWidget(options)
    });
  }
};
