{{- define "guestbook.name" -}}
{{ .Chart.Name }}
{{- end -}}

{{- define "guestbook.labels" -}}
app.kubernetes.io/name: {{ include "guestbook.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
