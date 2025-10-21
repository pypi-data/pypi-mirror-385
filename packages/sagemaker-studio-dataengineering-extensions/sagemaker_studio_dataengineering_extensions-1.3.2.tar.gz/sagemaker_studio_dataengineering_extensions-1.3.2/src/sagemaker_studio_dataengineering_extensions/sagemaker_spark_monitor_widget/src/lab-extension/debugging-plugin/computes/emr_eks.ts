import { SageMakerConnectionDetails, startSparkHistoryServer } from "../utils/jupyter_api_client"
import { LINK_TYPE_DRIVER_LOG, LINK_TYPE_SPARK_UI } from '../constants';
import { Environment } from "../utils/environment";
import { CreatePresignedDomainUrlCommand, CreatePresignedDomainUrlResponse } from '@aws-sdk/client-sagemaker';
import { generatePresignedUrl } from "../utils/s3_utils";
import { createSMClient } from "../utils/aws_client_utils"

export async function handleEMRonEksDebuggingLinksClicked(connectionDetail: SageMakerConnectionDetails,
                                                          linkType: string,
                                                          logsLocation: string): Promise<void> {

  const env = await Environment.getInstance().getEnvironmentMetadata();
  return new Promise((resolve, reject) => {
    if (linkType == LINK_TYPE_SPARK_UI) {
      startSparkHistoryServer(logsLocation)
      .then(response => {
        if (response.status == "running" || response.status == "started") {
          const sagemakerClient = createSMClient(connectionDetail, env.dz_stage);
          const params = {
            DomainId: env.sm_domain_id,
            UserProfileName: env.user_id,
            LandingUri: "app:JupyterLab:proxy/18080/?showIncomplete=true",
            SpaceName: env.sm_space_name
          };
          const command = new CreatePresignedDomainUrlCommand(params);
          sagemakerClient.send(command)
          .then((response: CreatePresignedDomainUrlResponse) => {
            window.open(response.AuthorizedUrl, '_blank');
            resolve();
          })
          .catch((err: any) => {
            reject(err);
          });
        } else {
          throw new Error(`Error Starting the spark history server: ${response.message}`);
        }
      })
      .catch(err => {
        console.error('Error while launching the history server:', err);
        reject(err);
      })
    } else if (linkType == LINK_TYPE_DRIVER_LOG) {
      generatePresignedUrl(connectionDetail, logsLocation)
        .then(result => {
          window.open(result, '_blank');
          resolve();
        }).catch(err => {
          reject(err);
        })
    }
  });
}
