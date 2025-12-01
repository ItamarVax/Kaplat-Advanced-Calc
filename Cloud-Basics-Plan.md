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

### 2.1 AWS Account Setup
- [ ] Access AWS account (using MTA student license)
- [ ] Verify account has necessary permissions for:
  - ECR (Elastic Container Registry)
  - ECS (Elastic Container Service) or Elastic Beanstalk
  - IAM (for service roles)
- [ ] Set up billing alerts (if applicable) to monitor costs
- [ ] Choose AWS region (e.g., `us-east-1`, `eu-west-1`) - note this for later steps

### 2.2 Install AWS CLI
- [ ] Install AWS CLI v2:
  - **macOS**: `brew install awscli` or download from AWS website
  - **Windows**: Download MSI installer from AWS website
  - **Linux**: `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"`
- [ ] Verify installation: `aws --version`
- [ ] Configure AWS credentials:
  ```bash
  aws configure
  ```
  - Enter AWS Access Key ID
  - Enter AWS Secret Access Key
  - Enter default region (e.g., `us-east-1`)
  - Enter default output format (e.g., `json`)
- [ ] Test authentication: `aws sts get-caller-identity`

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
- [ ] Get your AWS account ID:
  ```bash
  aws sts get-caller-identity --query Account --output text
  ```
- [ ] Choose your AWS region (e.g., `us-east-1`, `eu-west-1`)
- [ ] Create ECR repository:
  ```bash
  aws ecr create-repository \
    --repository-name calculator-server \
    --region <YOUR_REGION>
  ```
- [ ] Note the repository URI (format: `<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/calculator-server`)
- [ ] Get login token and authenticate Docker:
  ```bash
  aws ecr get-login-password --region <YOUR_REGION> | \
    docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
  ```

### 4.3 Build and Push Docker Image to ECR
- [ ] Build Docker image:
  ```bash
  docker build -t calculator-server .
  ```
- [ ] Tag image for ECR:
  ```bash
  docker tag calculator-server:latest \
    <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/calculator-server:latest
  ```
- [ ] Push image to ECR:
  ```bash
  docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/calculator-server:latest
  ```
- [ ] Verify image in ECR:
  ```bash
  aws ecr describe-images --repository-name calculator-server --region <YOUR_REGION>
  ```

### 4.4 Deploy to ECS Fargate (Recommended Method)

#### 4.4.1 Create ECS Cluster
- [ ] Create Fargate cluster:
  ```bash
  aws ecs create-cluster --cluster-name calculator-cluster --region <YOUR_REGION>
  ```
- [ ] Or use AWS Console: ECS → Clusters → Create Cluster → Select "Fargate"

#### 4.4.2 Create Task Definition
- [ ] Create task definition JSON file (`task-definition.json`):
  ```json
  {
    "family": "calculator-server",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "containerDefinitions": [
      {
        "name": "calculator-server",
        "image": "<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/calculator-server:latest",
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
            "awslogs-group": "/ecs/calculator-server",
            "awslogs-region": "<YOUR_REGION>",
            "awslogs-stream-prefix": "ecs"
          }
        }
      }
    ]
  }
  ```
- [ ] Create CloudWatch log group:
  ```bash
  aws logs create-log-group --log-group-name /ecs/calculator-server --region <YOUR_REGION>
  ```
- [ ] Register task definition:
  ```bash
  aws ecs register-task-definition --cli-input-json file://task-definition.json --region <YOUR_REGION>
  ```

#### 4.4.3 Create ECS Service
- [ ] Create VPC and subnets (or use default):
  - Note: You may need to create a VPC, subnets, and security group
  - Or use default VPC: `aws ec2 describe-vpcs --filters "Name=isDefault,Values=true"`
- [ ] Create security group allowing inbound traffic on port 8496:
  ```bash
  aws ec2 create-security-group \
    --group-name calculator-sg \
    --description "Security group for calculator server" \
    --region <YOUR_REGION>
  ```
- [ ] Add inbound rule to security group:
  ```bash
  aws ec2 authorize-security-group-ingress \
    --group-id <SECURITY_GROUP_ID> \
    --protocol tcp \
    --port 8496 \
    --cidr 0.0.0.0/0 \
    --region <YOUR_REGION>
  ```
- [ ] Create Application Load Balancer (ALB) for public access:
  - Use AWS Console: EC2 → Load Balancers → Create Load Balancer
  - Select "Application Load Balancer"
  - Configure:
    - Scheme: Internet-facing
    - IP address type: IPv4
    - Listeners: HTTP on port 80 (forward to port 8496)
    - Target group: Create new (port 8496, protocol HTTP)
    - Health check: `/calculator/health`
- [ ] Get ALB ARN and target group ARN from console
- [ ] Create ECS service:
  ```bash
  aws ecs create-service \
    --cluster calculator-cluster \
    --service-name calculator-service \
    --task-definition calculator-server \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SECURITY_GROUP_ID>],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=<TARGET_GROUP_ARN>,containerName=calculator-server,containerPort=8496" \
    --region <YOUR_REGION>
  ```
- [ ] **Alternative: Use AWS Console** (easier for first-time setup):
  - ECS → Clusters → calculator-cluster → Services → Create
  - Configure service settings
  - Set desired count to 1 (for 24/7 availability)

#### 4.4.4 Get Public URL
- [ ] Get ALB DNS name:
  ```bash
  aws elbv2 describe-load-balancers --region <YOUR_REGION> --query 'LoadBalancers[?LoadBalancerName==`<ALB_NAME>`].DNSName' --output text
  ```
- [ ] Your public URL will be: `http://<ALB_DNS_NAME>`
- [ ] Test URL: `curl http://<ALB_DNS_NAME>/calculator/health`
- [ ] **Note**: For HTTPS, you'll need to configure SSL certificate (optional but recommended)

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
- [ ] **ECS Fargate**: Ensure service desired count = 1 (already set in step 4.4.3)
- [ ] **Elastic Beanstalk**: Configure environment to keep at least 1 instance running
- [ ] Set up health checks (already configured in ALB/EB)
- [ ] Monitor service status:
  ```bash
  aws ecs describe-services --cluster calculator-cluster --services calculator-service --region <YOUR_REGION>
  ```
- [ ] Verify service is running and healthy

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
  - Check task definition: `aws ecs describe-task-definition --task-definition calculator-server`
  - Review service events: `aws ecs describe-services --cluster calculator-cluster --services calculator-service`
  - Verify VPC and subnet configuration
  - Check security group rules

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

