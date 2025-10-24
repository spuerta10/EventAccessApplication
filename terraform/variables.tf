variable "region" {
    type = string
    default = "us-central1"
}

variable "db_tier" {
    type = string
    default = "db-f1-micro"
}

# db_port=5432 by default in Cloud SQL

# required vars

variable "project_id" {
    type = string
}

variable "environment" {
    type = string
}

# database vars

variable "db_user" {
    type = string
}

variable "db_password" {
    type = string
}

variable "db_name" {
    type = string
}

# cloud run vars
