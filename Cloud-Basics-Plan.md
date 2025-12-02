# Cloud Basics Exercise - Implementation Roadmap

## Overview
Deploy the Docker container from EX5 (calculator server) to a cloud provider and expose it 24/7 for automated testing. The automation will test endpoints like `/calculator/health` and expect responses matching the server logic from EX3.

**Submission Deadline**: 3.12.25  
**Submission Format**: Single JSON file (NOT zipped)

---

## Phase 1: Preparation & Assessment

### 1.1 Verify Existing Docker Setup
- [ ] Check if Dockerfile exists from EX5
- [ ] Verify Dockerfile is properly configured for the Flask server
- [ ] Ensure Dockerfile exposes the correct port (currently 8496, but can be changed)
- [ ] Test Docker container locally:
  ```bash
  docker build -t calculator-server .
  docker run -p 8496:8496 calculator-server
  ```
- [ ] Verify all endpoints work locally:
  - `GET /calculator/health` → should return "OK"
  - Test other endpoints to ensure functionality

### 1.2 Review Server Requirements
- [ ] Confirm server starts cleanly (no persistent state from previous runs)
- [ ] Verify all required endpoints are implemented:
  - `/calculator/health`
  - `/calculator/stack/*` endpoints
  - `/calculator/independent/*` endpoints
  - `/calculator/history`
  - `/logs/level` endpoints
- [ ] Ensure server binds to `0.0.0.0` (not `127.0.0.1`) for external access
- [ ] Check that server handles port configuration via environment variable (recommended for cloud deployment)

### 1.3 Code Adjustments for AWS
- [ ] **IMPORTANT**: Make port configurable via environment variable (AWS services may assign different ports)
  - Update `server.py` to read `PORT` environment variable, default to 8496
  - Example: `port = int(os.environ.get('PORT', 8496))`
- [ ] Ensure server doesn't rely on local file system for critical operations
- [ ] Verify logging doesn't break if log directories don't exist
- [ ] Test that server initializes with clean state (no leftover data)
- [ ] Update Dockerfile to use environment variable for port (if needed)

---

## Phase 2: AWS Setup & Configuration

**Note**: Since you already have AWS CLI installed and are using SSO login, you can skip the installation steps and proceed directly to verification.

### 2.1 AWS Account Setup
- [ ] **Verify SSO login status**:
  ```bash
  aws sts get-caller-identity
  ```
  - Should return your AWS account ID, user ARN, and user ID
  - If not logged in, run: `aws sso login`

- [ ] **Verify account has necessary permissions** for:
  - ECR (Elastic Container Registry)
  - ECS (Elastic Container Service) or Elastic Beanstalk
  - IAM (for service roles)
  - EC2 (for VPC, subnets, security groups)
  - Elastic Load Balancing (for ALB)
  - CloudWatch Logs (for logging)

- [ ] **Test permissions** (optional):
  ```bash
  # Test ECR access
  aws ecr describe-repositories --region us-east-1
  
  # Test ECS access
  aws ecs list-clusters --region us-east-1
  ```

- [ ] **Set up billing alerts** (if applicable) to monitor costs
- [ ] **Choose AWS region** (e.g., `us-east-1`, `eu-west-1`) - note this for later steps

### 2.2 Verify AWS CLI Setup (Already Installed)
- [ ] **Verify AWS CLI is installed**:
  ```bash
  aws --version
  # Should show: aws-cli/2.x.x Python/3.x.x Darwin/x.x.x source/x86_64
  ```

- [ ] **Verify SSO login status**:
  ```bash
  aws sts get-caller-identity
  ```
  - Should return your AWS account ID, user ARN, and user ID
  - If you get an error, you may need to re-authenticate (see below)

- [ ] **Re-authenticate with SSO** (if needed):
  ```bash
  aws sso login
  ```
  - This will open your browser for SSO authentication
  - After successful login, your session will be active

- [ ] **Check SSO session status**:
  ```bash
  aws sts get-caller-identity
  ```
  - Verify you're logged in and can see your account details

- [ ] **Set default region** (if not already set):
  ```bash
  # Check current region
  aws configure get region
  
  # Set default region (choose your preferred region)
  aws configure set region us-east-1
  # Or: aws configure set region eu-west-1
  # Or: aws configure set region us-west-2
  ```

- [ ] **View current configuration**:
  ```bash
  aws configure list
  ```

- [ ] **List available SSO profiles** (if you have multiple):
  ```bash
  cat ~/.aws/config
  # Look for [profile <profile-name>] sections
  ```

- [ ] **Use specific SSO profile** (if you have multiple profiles):
  ```bash
  # Set profile for current session
  export AWS_PROFILE=<your-profile-name>
  
  # Or use --profile flag with commands
  aws sts get-caller-identity --profile <your-profile-name>
  ```

- [ ] **Important: SSO Session Management**:
  - SSO sessions typically expire after a set time (e.g., 1-12 hours)
  - If you get authentication errors during deployment, re-authenticate:
    ```bash
    aws sso login
    ```
  - You can check session expiration:
    ```bash
    aws sts get-caller-identity
    # If this fails, your session has expired
    ```
  - For long-running deployments, ensure your SSO session is fresh before starting

### 2.3 AWS Services Overview
**Services you'll use:**
- **ECR (Elastic Container Registry)**: Store Docker images
- **ECS Fargate** or **Elastic Beanstalk**: Run containers (recommended: ECS Fargate for simplicity)
- **Application Load Balancer** (if needed): Expose service publicly
- **IAM**: Service roles and permissions

---

## Phase 3: Docker Container Preparation

### 3.1 Create/Update Dockerfile (if needed)
- [ ] Ensure Dockerfile uses appropriate base image (Python 3.9+)
- [ ] Copy all necessary files:
  - `server.py`
  - `calculator.py`
  - `errors.py`
  - `loggerBuilds.py`
  - `loggerRequests.py`
  - `requirements.txt`
- [ ] Install dependencies from `requirements.txt`
- [ ] Expose port (use environment variable for flexibility)
- [ ] Set working directory
- [ ] Configure startup command
- [ ] Ensure logs directory is created if needed

### 3.2 Dockerfile Best Practices
- [ ] Use multi-stage build if appropriate (optimize image size)
- [ ] Set non-root user for security
- [ ] Use `.dockerignore` to exclude unnecessary files
- [ ] Test Docker image builds successfully
- [ ] Verify image runs and responds to health checks

### 3.3 Local Testing
- [ ] Build Docker image: `docker build -t calculator-server .`
- [ ] Run container: `docker run -p 8496:8496 calculator-server`
- [ ] Test all endpoints from outside container
- [ ] Verify health endpoint: `curl http://localhost:8496/calculator/health`
- [ ] Test stack operations
- [ ] Test independent calculations
- [ ] Verify logging works correctly
- [ ] Ensure clean state on container restart

---

## Phase 4: AWS Deployment

### 4.1 Prepare Docker Image for AWS
- [ ] Ensure Dockerfile is ready (from Phase 3)
- [ ] Test local build: `docker build -t calculator-server .`
- [ ] Test locally: `docker run -p 8496:8496 calculator-server`
- [ ] Verify all endpoints work in container

### 4.2 Set Up ECR (Elastic Container Registry)

**Set variables for easier use (macOS terminal):**
```bash
# Set your AWS region (change to your preferred region)
export AWS_REGION="us-east-1"

# Get your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile <account-name> --query Account --output text)

# Set ECR repository name
export ECR_REPO_NAME="calculator-server"

# Set full ECR repository URI
export ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Display the values
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "ECR Repository URI: $ECR_REPO_URI"
```

- [ ] **Get your AWS account ID**:
  ```bash
  aws sts get-caller-identity --query Account --output text
  ```

- [ ] **Choose your AWS region** (e.g., `us-east-1`, `eu-west-1`, `us-west-2`):
  ```bash
  # List available regions
  aws ec2 describe-regions --query 'Regions[*].RegionName' --output text
  ```

- [ ] **Create ECR repository**:
  ```bash
  aws ecr create-repository \
    --repository-name calculator-server \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256
  ```

- [ ] **Verify repository was created**:
  ```bash
  aws ecr describe-repositories \
    --repository-names calculator-server \
    --region $AWS_REGION
  ```

- [ ] **Get login token and authenticate Docker**:
  ```bash
  aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_REPO_URI
  ```
  - Expected output: `Login Succeeded`

- [ ] **List ECR repositories** (to verify):
  ```bash
  aws ecr describe-repositories --region $AWS_REGION --output table
  ```

### 4.3 Build and Push Docker Image to ECR

**Make sure you've set the variables from section 4.2, or set them again:**
```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/calculator-server"
```

- [ ] **Build Docker image**:
  ```bash
  docker build -t calculator-server .
  ```

- [ ] **Verify image was built**:
  ```bash
  docker images | grep calculator-server
  ```

- [ ] **Tag image for ECR**:
  ```bash
  docker tag calculator-server:latest $ECR_REPO_URI:latest
  ```

- [ ] **Verify tagged image**:
  ```bash
  docker images | grep calculator-server
  ```

- [ ] **Push image to ECR**:
  ```bash
  docker push $ECR_REPO_URI:latest
  ```
  - This may take a few minutes depending on image size and internet speed

- [ ] **Verify image in ECR**:
  ```bash
  aws ecr describe-images \
    --repository-name calculator-server \
    --region $AWS_REGION \
    --output table
  ```

- [ ] **Get image details** (optional):
  ```bash
  aws ecr describe-images \
    --repository-name calculator-server \
    --image-ids imageTag=latest \
    --region $AWS_REGION \
    --query 'imageDetails[0]' \
    --output json
  ```

### 4.4 Deploy to ECS Fargate (Recommended Method)

#### 4.4.1 Create ECS Cluster

**Set cluster name variable:**
```bash
export CLUSTER_NAME="calculator-cluster"
```

- [ ] **Create Fargate cluster**:
  ```bash
  aws ecs create-cluster \
    --cluster-name $CLUSTER_NAME \
    --region $AWS_REGION \
    --capacity-providers FARGATE FARGATE_SPOT \
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
  ```

- [ ] **Verify cluster was created**:
  ```bash
  aws ecs describe-clusters \
    --clusters $CLUSTER_NAME \
    --region $AWS_REGION \
    --output table
  ```

- [ ] **List all clusters** (optional):
  ```bash
  aws ecs list-clusters --region $AWS_REGION --output table
  ```

#### 4.4.2 Create Task Definition

**Set task definition variables:**
```bash
export TASK_FAMILY="calculator-server"
export LOG_GROUP_NAME="/ecs/calculator-server"
```

- [ ] **Create CloudWatch log group** (required before task definition):
  ```bash
  aws logs create-log-group \
    --log-group-name $LOG_GROUP_NAME \
    --region $AWS_REGION
  ```

- [ ] **Verify log group was created**:
  ```bash
  aws logs describe-log-groups \
    --log-group-name-prefix "/ecs/" \
    --region $AWS_REGION \
    --output table
  ```

- [ ] **Create task definition JSON file** (`task-definition.json`):
  ```bash
  cat > task-definition.json <<EOF
  {
    "family": "$TASK_FAMILY",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskRole",
    "containerDefinitions": [
      {
        "name": "calculator-server",
        "image": "${ECR_REPO_URI}:latest",
        "essential": true,
        "portMappings": [
          {
            "containerPort": 8496,
            "protocol": "tcp"
          }
        ],
        "environment": [
          {
            "name": "PORT",
            "value": "8496"
          }
        ],
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "$LOG_GROUP_NAME",
            "awslogs-region": "$AWS_REGION",
            "awslogs-stream-prefix": "ecs"
          }
        }
      }
    ]
  }
  EOF
  ```

  **Note**: If you get IAM role errors, you may need to create the execution role first (see IAM setup below) or remove the `executionRoleArn` and `taskRoleArn` lines temporarily.

- [ ] **Create IAM execution role** (if it doesn't exist):
  ```bash
  # Create trust policy file
  cat > trust-policy.json <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ecs-tasks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF

  # Create the role
  aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file://trust-policy.json \
    --region $AWS_REGION

  # Attach the managed policy for ECS task execution
  aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
    --region $AWS_REGION
  ```

- [ ] **Register task definition**:
  ```bash
  aws ecs register-task-definition \
    --cli-input-json file://task-definition.json \
    --region $AWS_REGION
  ```

- [ ] **Verify task definition was created**:
  ```bash
  aws ecs describe-task-definition \
    --task-definition $TASK_FAMILY \
    --region $AWS_REGION \
    --query 'taskDefinition.[family,revision,status]' \
    --output table
  ```

- [ ] **List all task definitions** (optional):
  ```bash
  aws ecs list-task-definitions \
    --family-prefix $TASK_FAMILY \
    --region $AWS_REGION \
    --output table
  ```

#### 4.4.3 Create ECS Service

**Get VPC and subnet information:**
```bash
# Get default VPC ID
export VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query 'Vpcs[0].VpcId' \
  --output text \
  --region $AWS_REGION)

echo "VPC ID: $VPC_ID"

# Get subnet IDs in the default VPC (need at least 2 for ALB)
export SUBNET_IDS=$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[*].SubnetId' \
  --output text \
  --region $AWS_REGION)

echo "Subnet IDs: $SUBNET_IDS"

# Get first subnet ID (for single subnet deployment without ALB)
export SUBNET_ID=$(echo $SUBNET_IDS | awk '{print $1}')
echo "Using Subnet ID: $SUBNET_ID"
```

- [ ] **Get VPC and subnet information**:
  ```bash
  # List all VPCs
  aws ec2 describe-vpcs --region $AWS_REGION --output table
  
  # Get default VPC ID
  export VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' \
    --output text \
    --region $AWS_REGION)
  
  # Get subnet IDs
  export SUBNET_IDS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[*].SubnetId' \
    --output text \
    --region $AWS_REGION)
  
  # Get first subnet
  export SUBNET_ID=$(echo $SUBNET_IDS | awk '{print $1}')
  ```

- [ ] **Create security group**:
  ```bash
  export SG_NAME="calculator-sg"
  
  export SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SG_NAME \
    --description "Security group for calculator server" \
    --vpc-id $VPC_ID \
    --region $AWS_REGION \
    --query 'GroupId' \
    --output text)
  
  echo "Security Group ID: $SECURITY_GROUP_ID"
  ```

- [ ] **Add inbound rule to security group** (allow port 8496):
  ```bash
  aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 8496 \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION
  ```

- [ ] **Verify security group rules**:
  ```bash
  aws ec2 describe-security-groups \
    --group-ids $SECURITY_GROUP_ID \
    --region $AWS_REGION \
    --output table
  ```

- [ ] **Create Application Load Balancer (ALB)**:
  ```bash
  export ALB_NAME="calculator-alb"
  
  # Get at least 2 subnet IDs for ALB (ALB requires subnets in at least 2 AZs)
  export SUBNET_ID_1=$(echo $SUBNET_IDS | awk '{print $1}')
  export SUBNET_ID_2=$(echo $SUBNET_IDS | awk '{print $2}')
  
  # Create ALB
  export ALB_ARN=$(aws elbv2 create-load-balancer \
    --name $ALB_NAME \
    --subnets $SUBNET_ID_1 $SUBNET_ID_2 \
    --scheme internet-facing \
    --type application \
    --ip-address-type ipv4 \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)
  
  echo "ALB ARN: $ALB_ARN"
  
  # Get ALB DNS name
  export ALB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].DNSName' \
    --output text)
  
  echo "ALB DNS: $ALB_DNS"
  ```

- [ ] **Create target group**:
  ```bash
  export TG_NAME="calculator-tg"
  
  export TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
    --name $TG_NAME \
    --protocol HTTP \
    --port 8496 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path /calculator/health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --region $AWS_REGION \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)
  
  echo "Target Group ARN: $TARGET_GROUP_ARN"
  ```

- [ ] **Create listener for ALB** (forward port 80 to target group):
  ```bash
  aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN \
    --region $AWS_REGION
  ```

- [ ] **Create ECS service**:
  ```bash
  export SERVICE_NAME="calculator-service"
  
  aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition $TASK_FAMILY \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID_1,$SUBNET_ID_2],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$TARGET_GROUP_ARN,containerName=calculator-server,containerPort=8496" \
    --region $AWS_REGION
  ```

- [ ] **Verify service was created**:
  ```bash
  aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --output table
  ```

- [ ] **Check service status**:
  ```bash
  aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'services[0].[serviceName,status,runningCount,desiredCount]' \
    --output table
  ```

#### 4.4.4 Get Public URL

**Get ALB DNS name:**
```bash
# If you set ALB_DNS earlier, it's already available
# Otherwise, get it:
export ALB_DNS=$(aws elbv2 describe-load-balancers \
  --region $AWS_REGION \
  --query 'LoadBalancers[?LoadBalancerName==`calculator-alb`].DNSName' \
  --output text)

echo "Your public URL: http://$ALB_DNS"
```

- [ ] **Get ALB DNS name**:
  ```bash
  export ALB_DNS=$(aws elbv2 describe-load-balancers \
    --region $AWS_REGION \
    --query 'LoadBalancers[?LoadBalancerName==`calculator-alb`].DNSName' \
    --output text)
  
  echo "Public URL: http://$ALB_DNS"
  ```

- [ ] **Wait for service to be stable** (may take 2-5 minutes):
  ```bash
  # Check service status
  aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'services[0].events[0:3]' \
    --output table
  
  # Wait until running count equals desired count
  aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION
  ```

- [ ] **Test health endpoint**:
  ```bash
  curl http://$ALB_DNS/calculator/health
  ```
  - Expected response: `OK`

- [ ] **Test other endpoints**:
  ```bash
  # Test stack size
  curl http://$ALB_DNS/calculator/stack/size
  
  # Test independent calculation
  curl -X POST http://$ALB_DNS/calculator/independent/calculate \
    -H "Content-Type: application/json" \
    -d '{"operation": "plus", "arguments": [5, 3]}'
  ```

- [ ] **Your final submission URL will be**: `http://$ALB_DNS`
  - Make sure to note this down for your submission JSON file!

- [ ] **Optional: Set up HTTPS** (for production, not required for exercise):
  ```bash
  # This requires an SSL certificate from ACM (AWS Certificate Manager)
  # For the exercise, HTTP is sufficient
  ```

### 4.5 Alternative: Deploy to Elastic Beanstalk (Simpler Option)

#### 4.5.1 Install EB CLI
- [ ] Install Elastic Beanstalk CLI:
  ```bash
  pip install awsebcli
  ```
- [ ] Verify: `eb --version`

#### 4.5.2 Initialize and Deploy
- [ ] Initialize EB application:
  ```bash
  eb init -p docker calculator-server --region <YOUR_REGION>
  ```
- [ ] Create environment:
  ```bash
  eb create calculator-env
  ```
- [ ] Deploy:
  ```bash
  eb deploy
  ```
- [ ] Get URL:
  ```bash
  eb status
  ```
- [ ] Your URL will be: `http://<ENVIRONMENT_NAME>.elasticbeanstalk.com`

### 4.6 Configure for 24/7 Availability

- [ ] **Verify service desired count is 1** (for 24/7 availability):
  ```bash
  aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'services[0].[desiredCount,runningCount]' \
    --output table
  ```

- [ ] **Update service if needed** (ensure desired count = 1):
  ```bash
  aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --desired-count 1 \
    --region $AWS_REGION
  ```

- [ ] **Verify health checks are working**:
  ```bash
  # Check target group health
  aws elbv2 describe-target-health \
    --target-group-arn $TARGET_GROUP_ARN \
    --region $AWS_REGION \
    --output table
  ```

- [ ] **Monitor service status**:
  ```bash
  # Check service events
  aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'services[0].events[0:5]' \
    --output table
  ```

- [ ] **Check CloudWatch logs** (if issues occur):
  ```bash
  # View recent log streams
  aws logs describe-log-streams \
    --log-group-name $LOG_GROUP_NAME \
    --order-by LastEventTime \
    --descending \
    --max-items 5 \
    --region $AWS_REGION \
    --output table
  
  # Get recent log events
  export LOG_STREAM=$(aws logs describe-log-streams \
    --log-group-name $LOG_GROUP_NAME \
    --order-by LastEventTime \
    --descending \
    --max-items 1 \
    --region $AWS_REGION \
    --query 'logStreams[0].logStreamName' \
    --output text)
  
  aws logs get-log-events \
    --log-group-name $LOG_GROUP_NAME \
    --log-stream-name $LOG_STREAM \
    --limit 20 \
    --region $AWS_REGION \
    --output text
  ```

- [ ] **Set up CloudWatch alarms** (optional, for monitoring):
  ```bash
  # Create alarm for service not running
  aws cloudwatch put-metric-alarm \
    --alarm-name calculator-service-down \
    --alarm-description "Alert when calculator service is down" \
    --metric-name RunningTaskCount \
    --namespace AWS/ECS \
    --statistic Average \
    --period 60 \
    --threshold 1 \
    --comparison-operator LessThanThreshold \
    --evaluation-periods 1 \
    --region $AWS_REGION
  ```

---

## Phase 5: Post-Deployment Verification

### 5.1 URL Validation
- [ ] Verify URL starts with `http://` or `https://`
- [ ] Test URL is accessible from external network
- [ ] Document the full URL (will be used in submission)

### 5.2 Endpoint Testing
- [ ] Test health endpoint: `GET <URL>/calculator/health`
  - Expected: `OK` with status 200
- [ ] Test stack operations:
  - `GET <URL>/calculator/stack/size`
  - `PUT <URL>/calculator/stack/arguments`
  - `GET <URL>/calculator/stack/operate`
- [ ] Test independent calculations:
  - `POST <URL>/calculator/independent/calculate`
- [ ] Test history endpoint:
  - `GET <URL>/calculator/history`
- [ ] Test log level endpoints:
  - `GET <URL>/logs/level`
  - `PUT <URL>/logs/level`

### 5.3 Clean State Verification
- [ ] Verify server starts with clean state (no previous data)
- [ ] Test that restarting container/service clears history
- [ ] Ensure automation will see fresh instance

### 5.4 Availability Testing
- [ ] Verify service is running 24/7
- [ ] Test cold start time (if applicable)
- [ ] Configure minimum instances = 1 (if option available) to minimize cold starts
- [ ] Monitor service for a few hours to ensure stability

### 5.5 Performance Check
- [ ] Test response times
- [ ] Verify all endpoints respond correctly
- [ ] Check error handling works properly
- [ ] Ensure logging doesn't cause issues

---

## Phase 6: Submission Preparation

### 6.1 Gather Information
- [ ] Your full name
- [ ] Your student ID
- [ ] Final deployed URL (must start with http:// or https://)

### 6.2 Create Submission JSON
- [ ] Create a new JSON file (e.g., `submission.json`)
- [ ] Use exact format:
  ```json
  {
    "name": "Your Full Name",
    "id": "Your Student ID",
    "url": "https://your-deployed-url.com"
  }
  ```
- [ ] **CRITICAL**: Use double quotes (`"`) for all strings and keys
- [ ] **CRITICAL**: Ensure no trailing comma after last property
- [ ] **CRITICAL**: Keys must be exactly: `name`, `id`, `url` (case-sensitive)

### 6.3 Validate JSON
- [ ] Use online JSON validator: https://jsonlint.com/
- [ ] Copy entire JSON content
- [ ] Paste into validator
- [ ] Fix any syntax errors
- [ ] Verify JSON is valid before submission

### 6.4 Final Checks
- [ ] Verify URL is correct and accessible
- [ ] Test URL with `/calculator/health` endpoint
- [ ] Ensure URL starts with `http://` or `https://`
- [ ] Double-check name spelling
- [ ] Double-check student ID
- [ ] Verify JSON file is NOT zipped
- [ ] Test JSON file can be opened and parsed correctly

---

## Phase 7: Final Testing & Submission

### 7.1 Pre-Submission Testing
- [ ] Test all endpoints one more time
- [ ] Verify server responds correctly to automation-style requests
- [ ] Check that server state is clean (restart if needed)
- [ ] Verify URL is publicly accessible
- [ ] Test from different network (if possible)

### 7.2 Submission
- [ ] Ensure JSON file is valid (use jsonlint.com)
- [ ] Verify file is NOT zipped
- [ ] Submit JSON file before deadline (3.12.25)
- [ ] Keep URL active until after grading period

### 7.3 Post-Submission
- [ ] Monitor service for any issues
- [ ] Keep service running until grading is complete
- [ ] Document any issues encountered for future reference

---

## Important Notes & Warnings

### ⚠️ Critical Requirements
1. **JSON Format**: Must be valid JSON with double quotes. Use jsonlint.com to validate.
2. **URL Format**: Must start with `http://` or `https://` - automation takes it AS IS.
3. **Clean State**: Server must start fresh with no previous data/history.
4. **24/7 Availability**: Service must be accessible at all times.
5. **No Zipping**: Submit JSON file directly, NOT zipped.
6. **Case Sensitivity**: JSON keys must be exactly `name`, `id`, `url`.

### 📝 Key Endpoints to Test
- `GET /calculator/health` - Must return "OK"
- `GET /calculator/stack/size` - Stack operations
- `PUT /calculator/stack/arguments` - Push to stack
- `GET /calculator/stack/operate` - Perform operation
- `POST /calculator/independent/calculate` - Independent calculations
- `GET /calculator/history` - Operation history

### 🔧 AWS Troubleshooting Commands (macOS)

**Quick reference commands for troubleshooting:**

```bash
# Set variables (if not already set)
export AWS_REGION="us-east-1"
export CLUSTER_NAME="calculator-cluster"
export SERVICE_NAME="calculator-service"
export TASK_FAMILY="calculator-server"

# Check service status
aws ecs describe-services \
  --cluster $CLUSTER_NAME \
  --services $SERVICE_NAME \
  --region $AWS_REGION \
  --query 'services[0].[status,runningCount,desiredCount,events[0:3]]' \
  --output table

# List running tasks
aws ecs list-tasks \
  --cluster $CLUSTER_NAME \
  --service-name $SERVICE_NAME \
  --region $AWS_REGION

# Describe a specific task
export TASK_ARN=$(aws ecs list-tasks \
  --cluster $CLUSTER_NAME \
  --service-name $SERVICE_NAME \
  --region $AWS_REGION \
  --query 'taskArns[0]' \
  --output text)

aws ecs describe-tasks \
  --cluster $CLUSTER_NAME \
  --tasks $TASK_ARN \
  --region $AWS_REGION \
  --output json

# Check target group health
export TARGET_GROUP_ARN=$(aws elbv2 describe-target-groups \
  --names calculator-tg \
  --region $AWS_REGION \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

aws elbv2 describe-target-health \
  --target-group-arn $TARGET_GROUP_ARN \
  --region $AWS_REGION \
  --output table

# View CloudWatch logs
aws logs tail /ecs/calculator-server --follow --region $AWS_REGION
```

### 🔧 AWS Troubleshooting Tips
- **Port Issues**: 
  - Update server.py to use `PORT` environment variable
  - AWS ALB can forward port 80 to container port 8496
  - Verify port mapping in task definition matches container port
- **Cold Starts**: 
  - Set desired count = 1 in ECS service to keep instance running
  - Elastic Beanstalk keeps instances warm by default
- **CORS Issues**: 
  - Ensure server allows external requests (already configured with `host="0.0.0.0"`)
- **Health Check Failures**: 
  - Verify `/calculator/health` endpoint returns "OK" with 200 status
  - Check ALB target group health checks in AWS Console
  - Review CloudWatch logs: `/ecs/calculator-server`
- **Container Build Failures**: 
  - Check Dockerfile syntax and dependencies
  - Verify image builds locally before pushing to ECR
- **Deployment Failures**: 
  - Review ECS service events in AWS Console
  - Check CloudWatch logs for container errors
  - Verify security group allows inbound traffic on port 8496
  - Ensure task has proper IAM role for CloudWatch logging
- **ECR Authentication Issues**:
  - Re-authenticate: `aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com`
- **Service Not Starting**:
  ```bash
  # Check task definition
  aws ecs describe-task-definition \
    --task-definition calculator-server \
    --region $AWS_REGION \
    --output json
  
  # Review service events
  aws ecs describe-services \
    --cluster calculator-cluster \
    --services calculator-service \
    --region $AWS_REGION \
    --query 'services[0].events[0:10]' \
    --output table
  
  # Verify VPC and subnet configuration
  aws ec2 describe-vpcs --region $AWS_REGION --output table
  aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --region $AWS_REGION --output table
  
  # Check security group rules
  aws ec2 describe-security-groups \
    --group-ids $SECURITY_GROUP_ID \
    --region $AWS_REGION \
    --output table
  ```

- **View Real-time Logs**:
  ```bash
  # Tail CloudWatch logs in real-time
  aws logs tail /ecs/calculator-server --follow --region $AWS_REGION
  
  # Or view recent logs
  aws logs tail /ecs/calculator-server --since 10m --region $AWS_REGION
  ```

- **Restart Service** (if needed):
  ```bash
  # Force new deployment
  aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --force-new-deployment \
    --region $AWS_REGION
  ```

- **Delete and Recreate** (if everything fails):
  ```bash
  # Delete service
  aws ecs delete-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --force \
    --region $AWS_REGION
  
  # Then recreate using commands from section 4.4.3
  ```

### 📚 AWS Resources
- JSON Validator: https://jsonlint.com/
- AWS Documentation:
  - ECS Fargate: https://docs.aws.amazon.com/ecs/latest/developerguide/AWS_Fargate.html
  - ECR: https://docs.aws.amazon.com/ecr/
  - Elastic Beanstalk: https://docs.aws.amazon.com/elasticbeanstalk/
  - Application Load Balancer: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/
- AWS CLI Reference: https://docs.aws.amazon.com/cli/latest/reference/
- AWS Console: https://console.aws.amazon.com/

---

## Timeline Recommendation

- **Week 1**: Phase 1-2 (Preparation & Cloud Setup)
- **Week 2**: Phase 3-4 (Docker & Deployment)
- **Week 3**: Phase 5-6 (Testing & Submission Prep)
- **Before Deadline**: Phase 7 (Final Testing & Submission)

**Start early** to allow time for troubleshooting and learning cloud provider specifics!

---

## Quick Reference: AWS CLI Commands for macOS

### Initial Setup (Run Once)

```bash
# 1. Verify AWS CLI is installed (already done)
aws --version

# 2. Verify SSO login (re-authenticate if needed)
aws sts get-caller-identity
# If you get an error, run: aws sso login

# 3. Set all variables (copy-paste this block)
export AWS_REGION="us-east-1"  # Change to your preferred region
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export CLUSTER_NAME="calculator-cluster"
export SERVICE_NAME="calculator-service"
export TASK_FAMILY="calculator-server"
export ECR_REPO_NAME="calculator-server"
export ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"
export LOG_GROUP_NAME="/ecs/calculator-server"
export VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text --region $AWS_REGION)
export SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text --region $AWS_REGION)
export SUBNET_ID_1=$(echo $SUBNET_IDS | awk '{print $1}')
export SUBNET_ID_2=$(echo $SUBNET_IDS | awk '{print $2}')
export SG_NAME="calculator-sg"
export ALB_NAME="calculator-alb"
export TG_NAME="calculator-tg"

# Display all variables
echo "=== AWS Configuration ==="
echo "Region: $AWS_REGION"
echo "Account ID: $AWS_ACCOUNT_ID"
echo "VPC ID: $VPC_ID"
echo "ECR URI: $ECR_REPO_URI"
echo "========================"
```

### Complete Deployment Workflow

```bash
# Step 1: Create ECR repository
aws ecr create-repository --repository-name calculator-server --region $AWS_REGION

# Step 2: Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REPO_URI

# Step 3: Build, tag, and push Docker image
docker build -t calculator-server .
docker tag calculator-server:latest $ECR_REPO_URI:latest
docker push $ECR_REPO_URI:latest

# Step 4: Create ECS cluster
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION

# Step 5: Create CloudWatch log group
aws logs create-log-group --log-group-name $LOG_GROUP_NAME --region $AWS_REGION

# Step 6: Create task definition (create task-definition.json first - see section 4.4.2)
aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION

# Step 7: Create security group
export SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name $SG_NAME \
  --description "Security group for calculator server" \
  --vpc-id $VPC_ID \
  --region $AWS_REGION \
  --query 'GroupId' --output text)

# Step 8: Add security group rule
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp --port 8496 --cidr 0.0.0.0/0 --region $AWS_REGION

# Step 9: Create Application Load Balancer
export ALB_ARN=$(aws elbv2 create-load-balancer \
  --name $ALB_NAME \
  --subnets $SUBNET_ID_1 $SUBNET_ID_2 \
  --scheme internet-facing --type application --ip-address-type ipv4 \
  --region $AWS_REGION \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# Step 10: Create target group
export TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
  --name $TG_NAME \
  --protocol HTTP --port 8496 --vpc-id $VPC_ID --target-type ip \
  --health-check-path /calculator/health \
  --region $AWS_REGION \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

# Step 11: Create ALB listener
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN \
  --region $AWS_REGION

# Step 12: Create ECS service
aws ecs create-service \
  --cluster $CLUSTER_NAME \
  --service-name $SERVICE_NAME \
  --task-definition $TASK_FAMILY \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID_1,$SUBNET_ID_2],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=$TARGET_GROUP_ARN,containerName=calculator-server,containerPort=8496" \
  --region $AWS_REGION

# Step 13: Get public URL
export ALB_DNS=$(aws elbv2 describe-load-balancers \
  --region $AWS_REGION \
  --query 'LoadBalancers[?LoadBalancerName==`calculator-alb`].DNSName' \
  --output text)

echo "Your public URL: http://$ALB_DNS"

# Step 14: Wait for service to be stable
aws ecs wait services-stable \
  --cluster $CLUSTER_NAME \
  --services $SERVICE_NAME \
  --region $AWS_REGION

# Step 15: Test the endpoint
curl http://$ALB_DNS/calculator/health
```

### Useful Monitoring Commands

```bash
# Check service status
aws ecs describe-services \
  --cluster $CLUSTER_NAME \
  --services $SERVICE_NAME \
  --region $AWS_REGION \
  --query 'services[0].[status,runningCount,desiredCount]' \
  --output table

# Check target group health
aws elbv2 describe-target-health \
  --target-group-arn $TARGET_GROUP_ARN \
  --region $AWS_REGION \
  --output table

# View recent logs
aws logs tail $LOG_GROUP_NAME --since 10m --region $AWS_REGION

# Follow logs in real-time
aws logs tail $LOG_GROUP_NAME --follow --region $AWS_REGION
```

### Cleanup Commands (If You Need to Start Over)

```bash
# Delete ECS service
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $SERVICE_NAME \
  --desired-count 0 \
  --region $AWS_REGION

aws ecs delete-service \
  --cluster $CLUSTER_NAME \
  --service $SERVICE_NAME \
  --region $AWS_REGION

# Delete load balancer
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN --region $AWS_REGION

# Delete target group
aws elbv2 delete-target-group --target-group-arn $TARGET_GROUP_ARN --region $AWS_REGION

# Delete security group
aws ec2 delete-security-group --group-id $SECURITY_GROUP_ID --region $AWS_REGION

# Delete ECS cluster
aws ecs delete-cluster --cluster $CLUSTER_NAME --region $AWS_REGION

# Delete ECR repository (and all images)
aws ecr delete-repository \
  --repository-name calculator-server \
  --force \
  --region $AWS_REGION

# Delete CloudWatch log group
aws logs delete-log-group --log-group-name $LOG_GROUP_NAME --region $AWS_REGION
```

**Note**: Replace all `<VARIABLE>` placeholders with actual values or use the exported variables from the setup section above.

