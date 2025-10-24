variable "region" {
    type = string
    default = "us-central1"
}

variable "db_tier" {
    type = string
    default = "db-f1-micro"
}

variable "service_name" { # cloud run service name
    type = string
    default = "register-ticket-api"
}

# db_port=5432 by default in Cloud SQL

# required vars

variable "project_id" {
    type = string
}

variable "environment" {
    type = string
}

# --- artifact registry vars ---

variable "registry_id" {
    type=string
}

# --- database vars ---

variable "db_user" {
    type = string
}

variable "db_password" {
    type = string
}

variable "db_name" {
    type = string
}

# --- cloud run vars ---

variable "image_uri" {
    type = string
}