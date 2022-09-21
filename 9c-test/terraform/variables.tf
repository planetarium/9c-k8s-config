variable "name" {
  description = "general name for cluster related resources."
  default     = "9c-test"
}

variable "vpc_id" {
  description = "VPC ID"
  default     = "vpc-0ca5c72f48fdd131b"
}

variable "public_subnets" {
  description = "public subnet IDs for cluster related resources."
  default     = ["subnet-0ca96dde71e1769ec", "subnet-0cd61e38c9a58210d", "subnet-09af06d47e1c87153"]
}
