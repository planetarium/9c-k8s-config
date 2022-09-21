terraform {
  backend "s3" {
    bucket = "terraform-eks-backend"
    key    = "eks/9c-test"
    region = "us-east-2"
  }
}
