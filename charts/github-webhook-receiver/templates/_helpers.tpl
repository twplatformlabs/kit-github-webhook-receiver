{{/*
Expand the name of the chart.
*/}}
{{- define "github-webhook-receiver.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "github-webhook-receiver.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "github-webhook-receiver.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "github-webhook-receiver.labels" -}}
app: {{ include "github-webhook-receiver.name" . }}
version: {{ .Values.image.tag }}
env: {{ .Release.Namespace }}
helm.sh/chart: {{ include "github-webhook-receiver.chart" . }}
{{ include "github-webhook-receiver.selectorLabels" . }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "github-webhook-receiver.selectorLabels" -}}
app.kubernetes.io/name: {{ include "github-webhook-receiver.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "github-webhook-receiver.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "github-webhook-receiver.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
