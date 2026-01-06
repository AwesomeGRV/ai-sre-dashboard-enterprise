const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-otlp-grpc');
const { PrometheusExporter } = require('@opentelemetry/exporter-prometheus');

// Initialize the SDK
const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://otel:4317',
  }),
  metricExporter: new PrometheusExporter({
    port: 9464,
    endpoint: '/metrics',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: 'sample-sre-app',
  serviceVersion: '1.0.0',
});

sdk.start();

console.log('OpenTelemetry initialized with Prometheus exporter on port 9464');
