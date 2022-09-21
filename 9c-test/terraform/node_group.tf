resource "aws_eks_node_group" "node_group" {
  cluster_name    = aws_eks_cluster.cluster.name
  node_group_name = "eks-${var.name}"
  node_role_arn   = aws_iam_role.node_group.arn
  subnet_ids      = var.public_subnets
  instance_types  = ["c5.xlarge"]

  scaling_config {
    desired_size = 10
    max_size     = 20
    min_size     = 10
  }

  update_config {
    max_unavailable = 1
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks-AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.eks-AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.eks-AmazonEC2ContainerRegistryReadOnly,
  ]
}
