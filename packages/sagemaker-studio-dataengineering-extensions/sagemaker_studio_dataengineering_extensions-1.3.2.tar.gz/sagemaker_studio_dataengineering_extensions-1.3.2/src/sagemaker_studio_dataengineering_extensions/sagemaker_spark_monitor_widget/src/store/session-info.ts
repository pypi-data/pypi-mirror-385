/**
 * Session information interface for Spark UI integration
 * This matches the session info structure sent from SparkInfoReporter backend
 * 
 * Field usage by compute type:
 * - SPARK_GLUE: Uses session_id (e.g., 'dd7pqpq8i209e8-e8c354bc-c6cc-40f0-a950-0190e8cce7e7')
 * - SPARK_EMR_EC2: Uses application_id (e.g., 'application_1752107075835_0001')
 * - SPARK_EMR_SERVERLESS: Uses application_id for Job Run ID (e.g., '00ftv7na4881kh0m'), session_id is expected to be numbers
 * - SPARK_EMR_EKS: Uses application_id (e.g., 'spark-af8a2f1ca02544fbaa640d7d6e9755aa')
 * 
 * TODO: Consider consolidating session_id and application_id into a single 'spark_execution_id' field
 * since they all represent the same concept: the unique identifier for Spark UI access.
 */
export interface SessionInfo {
  connection_type: 'SPARK_GLUE' | 'SPARK_EMR_EC2' | 'SPARK_EMR_SERVERLESS' | 'SPARK_EMR_EKS';
  connection_name: string;
  
  // Compute-specific identifiers (could be consolidated)
  session_id?: string | number;    // Used by Glue (string), EMR Serverless (number)
  application_id?: string | number; // Used by EMR EC2 (string) and EMR Serverless (Job Run ID string) and EKS (string)

  // Allow additional connection-specific properties
  [key: string]: any;
}