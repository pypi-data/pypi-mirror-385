# Traefik Provider Guide

Umfassende Dokumentation für die Verwendung von Traefik mit GAL.

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Schnellstart](#schnellstart)
3. [Installation und Setup](#installation-und-setup)
4. [Konfigurationsoptionen](#konfigurationsoptionen)
5. [Feature-Implementierungen](#feature-implementierungen)
6. [Provider-Vergleich](#provider-vergleich)
7. [Traefik-spezifische Details](#traefik-spezifische-details)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Zusammenfassung](#zusammenfassung)

---

## Übersicht

**Traefik** ist ein modernes HTTP-Reverse-Proxy und Load Balancer, das speziell für Cloud-Native-Umgebungen entwickelt wurde. Es bietet automatische Service-Discovery, Let's Encrypt-Integration und ein benutzerfreundliches Dashboard.

### Warum Traefik?

- **🔄 Auto-Discovery**: Automatische Erkennung von Services (Docker, Kubernetes, Consul)
- **🔒 Let's Encrypt**: Native HTTPS mit automatischer Zertifikatserneuerung
- **📊 Dashboard**: Echtzeit-Monitoring und Konfigurationsvisualisierung
- **☁️ Cloud-Native**: Docker, Kubernetes, Swarm, Mesos, Consul, etcd, Zookeeper
- **⚡ Zero-Downtime**: Hot-Reload ohne Verbindungsabbruch
- **🎯 Middleware-System**: Flexible Request/Response-Manipulation

### Feature-Matrix

| Feature | Traefik Support | GAL Implementation |
|---------|-----------------|-------------------|
| Load Balancing | ✅ Vollständig | `upstream.load_balancer` |
| Active Health Checks | ✅ Native | `upstream.health_check.active` |
| Passive Health Checks | ⚠️ Limitiert | `upstream.health_check.passive` |
| Rate Limiting | ✅ rateLimit Middleware | `route.rate_limit` |
| Authentication | ✅ Basic, JWT (Traefik Plus) | `route.authentication` |
| CORS | ✅ headers Middleware | `route.cors` |
| Timeout & Retry | ✅ serversTransport, retry | `route.timeout`, `route.retry` |
| Circuit Breaker | ✅ circuitBreaker Middleware | `upstream.circuit_breaker` |
| WebSocket | ✅ Native | `route.websocket` |
| Header Manipulation | ✅ headers Middleware | `route.headers` |
| Body Transformation | ❌ Nicht nativ | `route.body_transformation` |

**Bewertung**: ✅ = Vollständig unterstützt | ⚠️ = Teilweise unterstützt | ❌ = Nicht unterstützt

---

## Schnellstart

### Beispiel 1: Basic Load Balancing

```yaml
services:
  - name: api_service
    protocol: http
    upstream:
      targets:
        - host: api-1.internal
          port: 8080
        - host: api-2.internal
          port: 8080
      load_balancer:
        algorithm: round_robin
    routes:
      - path_prefix: /api
```

**Generierte Traefik-Konfiguration:**

```yaml
http:
  routers:
    api_service_router_0:
      rule: "PathPrefix(`/api`)"
      service: api_service
  services:
    api_service:
      loadBalancer:
        servers:
          - url: "http://api-1.internal:8080"
          - url: "http://api-2.internal:8080"
```

### Beispiel 2: Basic Auth + Rate Limiting

```yaml
services:
  - name: secure_api
    protocol: http
    upstream:
      host: api.internal
      port: 8080
    routes:
      - path_prefix: /api
        authentication:
          enabled: true
          type: basic
          basic_auth:
            users:
              admin: password123
        rate_limit:
          enabled: true
          requests_per_second: 100
```

**Generierte Traefik-Konfiguration:**

```yaml
http:
  routers:
    secure_api_router_0:
      rule: "PathPrefix(`/api`)"
      service: secure_api
      middlewares:
        - secure_api_router_0_auth
        - secure_api_router_0_ratelimit

  middlewares:
    secure_api_router_0_auth:
      basicAuth:
        users:
          - "admin:$apr1$..."  # Hashed password

    secure_api_router_0_ratelimit:
      rateLimit:
        average: 100
        burst: 200

  services:
    secure_api:
      loadBalancer:
        servers:
          - url: "http://api.internal:8080"
```

### Beispiel 3: Complete Production Setup

```yaml
services:
  - name: production_api
    protocol: http
    upstream:
      targets:
        - host: api-1.internal
          port: 8080
        - host: api-2.internal
          port: 8080
      load_balancer:
        algorithm: round_robin
      health_check:
        active:
          enabled: true
          path: /health
          interval: 5s
      circuit_breaker:
        enabled: true
        max_failures: 5
    routes:
      - path_prefix: /api
        rate_limit:
          enabled: true
          requests_per_second: 100
        timeout:
          connect: 5s
          read: 30s
        retry:
          enabled: true
          attempts: 3
        cors:
          enabled: true
          allowed_origins: ["https://app.example.com"]
```

---

## Installation und Setup

### Docker (Empfohlen)

```bash
# Traefik mit Docker starten
docker run -d \
  --name traefik \
  -p 80:80 \
  -p 443:443 \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/traefik.yml:/etc/traefik/traefik.yml \
  traefik:latest
```

### Docker Compose

```yaml
version: "3"
services:
  traefik:
    image: traefik:latest
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik.yml:/etc/traefik/traefik.yml
      - ./dynamic-config.yml:/etc/traefik/dynamic-config.yml
    command:
      - "--api.dashboard=true"
      - "--providers.file.filename=/etc/traefik/dynamic-config.yml"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
```

### Kubernetes (Helm)

```bash
# Traefik Helm Repository hinzufügen
helm repo add traefik https://traefik.github.io/charts
helm repo update

# Traefik Ingress Controller installieren
helm install traefik traefik/traefik \
  --namespace traefik \
  --create-namespace \
  --set dashboard.enabled=true \
  --set service.type=LoadBalancer
```

### GAL-Konfiguration generieren

```bash
# Traefik-Konfiguration generieren
gal generate --config config.yaml --provider traefik --output traefik-dynamic.yml

# Oder via Docker
docker run --rm -v $(pwd):/app ghcr.io/pt9912/x-gal:latest \
  generate --config config.yaml --provider traefik --output traefik-dynamic.yml
```

### Konfiguration anwenden

```bash
# Static Configuration (traefik.yml)
cat > traefik.yml <<EOF
api:
  dashboard: true

providers:
  file:
    filename: /etc/traefik/dynamic-config.yml
    watch: true

entrypoints:
  web:
    address: ":80"
  websecure:
    address: ":443"
EOF

# Dynamic Configuration (von GAL generiert)
cp traefik-dynamic.yml /etc/traefik/dynamic-config.yml

# Traefik starten/neu laden
docker restart traefik

# Dashboard öffnen: http://localhost:8080
```

---

## Konfigurationsoptionen

### Global Config

```yaml
global:
  host: 0.0.0.0
  port: 80
  log_level: info
```

**Traefik Mapping (traefik.yml):**

```yaml
entryPoints:
  web:
    address: ":80"

log:
  level: INFO
```

### Upstream Config

```yaml
services:
  - name: my_service
    upstream:
      targets:
        - host: backend-1.internal
          port: 8080
        - host: backend-2.internal
          port: 8080
      load_balancer:
        algorithm: round_robin
      health_check:
        active:
          enabled: true
          path: /health
```

**Traefik Mapping:**

```yaml
http:
  services:
    my_service:
      loadBalancer:
        servers:
          - url: "http://backend-1.internal:8080"
          - url: "http://backend-2.internal:8080"
        healthCheck:
          path: /health
          interval: 5s
```

### Route Config

```yaml
routes:
  - path_prefix: /api
    rate_limit:
      enabled: true
      requests_per_second: 100
```

**Traefik Mapping:**

```yaml
http:
  routers:
    my_service_router_0:
      rule: "PathPrefix(`/api`)"
      service: my_service
      middlewares:
        - my_service_router_0_ratelimit

  middlewares:
    my_service_router_0_ratelimit:
      rateLimit:
        average: 100
        burst: 200
```

---

## Feature-Implementierungen

### 1. Load Balancing

Traefik unterstützt mehrere Load-Balancing-Algorithmen über `loadBalancer.sticky`:

| GAL Algorithm | Traefik Implementation | Beschreibung |
|---------------|------------------------|--------------|
| `round_robin` | Default (keine Config) | Gleichmäßige Verteilung |
| `least_conn` | ⚠️ Nicht verfügbar | Traefik wählt zufällig |
| `ip_hash` | `sticky.cookie` | Session Persistence via Cookie |
| `weighted` | `servers.weight` | Gewichtete Verteilung |

**Implementierung** (gal/providers/traefik.py:230-261):

```python
# Services
output.append("  services:")
for service in config.services:
    output.append(f"    {service.name}:")
    output.append("      loadBalancer:")
    output.append("        servers:")

    # Targets
    if service.upstream:
        if service.upstream.targets:
            for target in service.upstream.targets:
                weight = target.weight if target.weight else 1
                url = f"http://{target.host}:{target.port}"
                output.append(f"          - url: \"{url}\"")
                if weight != 1:
                    output.append(f"            weight: {weight}")
```

**Sticky Sessions** (gal/providers/traefik.py:425):

```python
# Sticky sessions (IP hash)
if service.upstream and service.upstream.load_balancer:
    if service.upstream.load_balancer.algorithm == "ip_hash":
        output.append("        sticky:")
        output.append("          cookie:")
        output.append("            name: lb")
```

**Beispiel:**

```yaml
upstream:
  targets:
    - host: api-1.internal
      port: 8080
      weight: 3
    - host: api-2.internal
      port: 8080
      weight: 1
  load_balancer:
    algorithm: weighted
```

### 2. Health Checks

Traefik bietet Active Health Checks (Passive nur eingeschränkt über Circuit Breaker).

**Active Health Checks** (gal/providers/traefik.py:262-277):

```python
# Health checks
if service.upstream and service.upstream.health_check:
    hc = service.upstream.health_check
    if hc.active and hc.active.enabled:
        output.append("        healthCheck:")
        output.append(f"          path: {hc.active.path}")
        output.append(
            f"          interval: {hc.active.interval}"
        )
        output.append(
            f"          timeout: {hc.active.timeout}"
        )
```

**Passive Health Checks**: Traefik hat keine native passive health checks. Nutze Circuit Breaker als Alternative.

**Beispiel:**

```yaml
upstream:
  health_check:
    active:
      enabled: true
      path: /health
      interval: 5s
      timeout: 3s
      healthy_threshold: 2
      unhealthy_threshold: 3
```

### 3. Rate Limiting

Traefik verwendet das `rateLimit` Middleware.

**Implementierung** (gal/providers/traefik.py:347-359):

```python
# Rate limiting middlewares (route-level)
for service in config.services:
    for i, route in enumerate(service.routes):
        if route.rate_limit and route.rate_limit.enabled:
            router_name = f"{service.name}_router_{i}"
            rl = route.rate_limit
            output.append(f"    {router_name}_ratelimit:")
            output.append("      rateLimit:")
            output.append(f"        average: {rl.requests_per_second}")
            burst = (
                rl.burst if rl.burst else rl.requests_per_second * 2
            )
            output.append(f"        burst: {burst}")
```

**Beispiel:**

```yaml
routes:
  - path_prefix: /api
    rate_limit:
      enabled: true
      requests_per_second: 100
      burst: 200
```

**Generierte Middleware:**

```yaml
middlewares:
  api_service_router_0_ratelimit:
    rateLimit:
      average: 100  # Requests pro Sekunde
      burst: 200    # Burst-Kapazität
```

### 4. Authentication

Traefik unterstützt Basic Auth nativ, JWT nur in Traefik Enterprise.

**Basic Authentication** (gal/providers/traefik.py:361-377):

```python
# Basic auth middlewares
for service in config.services:
    for i, route in enumerate(service.routes):
        if route.authentication and route.authentication.enabled:
            auth = route.authentication
            if auth.type == "basic":
                router_name = f"{service.name}_router_{i}"
                output.append(f"    {router_name}_auth:")
                output.append("      basicAuth:")
                output.append("        users:")
                if auth.basic_auth and auth.basic_auth.users:
                    for username, password in auth.basic_auth.users.items():
                        # htpasswd-Format erforderlich
                        output.append(f'          - "{username}:$apr1$..."')
```

**JWT Authentication**: Traefik Open Source hat keine native JWT-Unterstützung. Nutze Traefik Enterprise oder ForwardAuth Middleware mit externem Service.

**Beispiel:**

```yaml
routes:
  - path_prefix: /api
    authentication:
      enabled: true
      type: basic
      basic_auth:
        users:
          admin: password123
          user: pass456
```

### 5. CORS

Traefik verwendet das `headers` Middleware für CORS.

**Implementierung** (gal/providers/traefik.py:379-409):

```python
# CORS middlewares
for service in config.services:
    for i, route in enumerate(service.routes):
        if route.cors and route.cors.enabled:
            router_name = f"{service.name}_router_{i}"
            cors = route.cors
            output.append(f"    {router_name}_cors:")
            output.append("      headers:")
            output.append("        accessControlAllowMethods:")
            for method in cors.allowed_methods or ["*"]:
                output.append(f"          - {method}")
            output.append("        accessControlAllowOriginList:")
            for origin in cors.allowed_origins:
                output.append(f"          - {origin}")
            if cors.allowed_headers:
                output.append("        accessControlAllowHeaders:")
                for header in cors.allowed_headers:
                    output.append(f"          - {header}")
            if cors.allow_credentials:
                output.append(
                    "        accessControlAllowCredentials: true"
                )
            if cors.max_age:
                output.append(
                    f"        accessControlMaxAge: {cors.max_age}"
                )
```

**Beispiel:**

```yaml
routes:
  - path_prefix: /api
    cors:
      enabled: true
      allowed_origins:
        - "https://app.example.com"
        - "https://admin.example.com"
      allowed_methods: ["GET", "POST", "PUT", "DELETE"]
      allowed_headers: ["Content-Type", "Authorization"]
      allow_credentials: true
      max_age: 86400
```

### 6. Timeout & Retry

**Timeout Configuration** (gal/providers/traefik.py:489-502):

```python
# Timeout (serversTransport)
has_timeout = any(
    route.timeout for service in config.services for route in service.routes
)
if has_timeout:
    output.append("  serversTransports:")
    output.append("    default:")
    for service in config.services:
        for route in service.routes:
            if route.timeout:
                timeout = route.timeout
                output.append("        serversTransport:")
                output.append("          forwardingTimeouts:")
                output.append(f"            dialTimeout: {timeout.connect}")
                output.append(
                    f"            responseHeaderTimeout: {timeout.read}"
                )
                output.append(f"            idleConnTimeout: {timeout.idle}")
                break
```

**Retry Configuration** (gal/providers/traefik.py:411-422):

```python
# Retry middlewares (route-level)
for service in config.services:
    for i, route in enumerate(service.routes):
        if route.retry and route.retry.enabled:
            router_name = f"{service.name}_router_{i}"
            retry = route.retry
            output.append(f"    {router_name}_retry:")
            output.append("      retry:")
            output.append(f"        attempts: {retry.attempts}")
            output.append(
                f"        initialInterval: {retry.base_interval}"
            )
```

**Beispiel:**

```yaml
routes:
  - path_prefix: /api
    timeout:
      connect: 5s
      read: 30s
      idle: 300s
    retry:
      enabled: true
      attempts: 3
      base_interval: 100ms
```

### 7. Circuit Breaker

Traefik verwendet das `circuitBreaker` Middleware.

**Implementierung** (gal/providers/traefik.py:424-445):

```python
# Circuit breaker middlewares
for service in config.services:
    if service.upstream and service.upstream.circuit_breaker:
        cb = service.upstream.circuit_breaker
        if cb.enabled:
            output.append(f"    {service.name}_circuitbreaker:")
            output.append("      circuitBreaker:")
            # Traefik verwendet expression syntax
            # z.B. "NetworkErrorRatio() > 0.30" oder "ResponseCodeRatio(500, 600, 0, 600) > 0.25"
            failure_ratio = (
                cb.max_failures / 100
            )  # Convert to percentage
            output.append(
                f'        expression: "NetworkErrorRatio() > {failure_ratio}"'
            )
```

**Beispiel:**

```yaml
upstream:
  circuit_breaker:
    enabled: true
    max_failures: 5  # 5% failure rate
    timeout: 30s
```

**Generierte Middleware:**

```yaml
middlewares:
  api_service_circuitbreaker:
    circuitBreaker:
      expression: "NetworkErrorRatio() > 0.05"
```

### 8. WebSocket

Traefik unterstützt WebSocket nativ ohne zusätzliche Konfiguration.

**Implementierung** (gal/providers/traefik.py:425):

```python
# WebSocket support (native in Traefik)
if route.websocket and route.websocket.enabled:
    output.append("        passHostHeader: true")
    output.append("        responseForwarding:")
    output.append("          flushInterval: 100ms")
```

**Beispiel:**

```yaml
routes:
  - path_prefix: /ws
    websocket:
      enabled: true
      idle_timeout: 300s
```

### 9. Header Manipulation

Traefik verwendet das `headers` Middleware für Request/Response Header Manipulation.

**Request Headers:**

```yaml
middlewares:
  api_service_router_0_headers:
    headers:
      customRequestHeaders:
        X-Request-ID: "{{uuid}}"
        X-Gateway: "GAL-Traefik"
```

**Response Headers:**

```yaml
middlewares:
  api_service_router_0_headers:
    headers:
      customResponseHeaders:
        X-Server: "Traefik"
        X-Response-Time: "{{timestamp}}"
```

**Beispiel:**

```yaml
routes:
  - path_prefix: /api
    headers:
      request:
        add:
          X-Request-ID: "{{uuid}}"
          X-Gateway: "GAL-Traefik"
        remove:
          - X-Internal-Header
      response:
        add:
          X-Server: "Traefik"
```

### 10. Body Transformation

⚠️ **Limitation**: Traefik Open Source unterstützt keine native Body Transformation.

**Alternativen**:

1. **ForwardAuth Middleware** mit externem Service:
```yaml
middlewares:
  body-transformer:
    forwardAuth:
      address: "http://transformer-service:8080/transform"
```

2. **Custom Traefik Plugin** (Go development erforderlich):
```go
// traefik-plugin-body-transformer
package traefik_plugin_body_transformer

func (t *BodyTransformer) ServeHTTP(rw http.ResponseWriter, req *http.Request) {
    // Body transformation logic
}
```

3. **Alternativer Provider**: Envoy, Kong, APISIX, Nginx, HAProxy unterstützen Body Transformation nativ.

**GAL Verhalten** (gal/providers/traefik.py:151-160):

```python
# Body Transformation warning
if route.body_transformation and route.body_transformation.enabled:
    logger.warning(
        f"Body transformation for route '{route.path_prefix}' "
        "is not natively supported by Traefik. Consider using:\n"
        "  1. ForwardAuth middleware with external transformation service\n"
        "  2. Custom Traefik plugin (requires Go development)\n"
        "  3. Alternative provider: Envoy, Kong, APISIX, Nginx, HAProxy"
    )
```

---

## Provider-Vergleich

| Feature | Traefik | Envoy | Kong | APISIX | Nginx | HAProxy |
|---------|---------|-------|------|--------|-------|---------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Auto-Discovery** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ | ⚠️ |
| **Let's Encrypt** | ⭐⭐⭐⭐⭐ | ⚠️ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⚠️ |
| **Dashboard** | ⭐⭐⭐⭐⭐ | ⚠️ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⚠️ | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Plugin System** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⚠️ | ⚠️ |

### Traefik vs Envoy
- **Traefik**: Einfacher, bessere Auto-Discovery, Let's Encrypt Integration
- **Envoy**: Mehr Features, bessere Observability, Service Mesh Integration

### Traefik vs Kong
- **Traefik**: Bessere Docker/Kubernetes Integration, Let's Encrypt, kostenlos
- **Kong**: Mehr Plugins, bessere Auth-Features, reiferes Ökosystem

### Traefik vs APISIX
- **Traefik**: Einfachere Konfiguration, besseres Dashboard, Let's Encrypt
- **APISIX**: Höhere Performance, mehr Plugins, Lua-Programmierbarkeit

### Traefik vs Nginx/HAProxy
- **Traefik**: Dynamische Konfiguration, Auto-Discovery, Dashboard, Let's Encrypt
- **Nginx/HAProxy**: Höhere Performance, niedriger Overhead, etablierter

---

## Traefik-spezifische Details

### Konfigurations-Struktur

Traefik verwendet zwei Konfigurationsdateien:

**1. Static Configuration (traefik.yml)**:
```yaml
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  file:
    filename: /etc/traefik/dynamic-config.yml
    watch: true
```

**2. Dynamic Configuration (dynamic-config.yml, von GAL generiert)**:
```yaml
http:
  routers:
    my_service_router_0:
      rule: "PathPrefix(`/api`)"
      service: my_service

  services:
    my_service:
      loadBalancer:
        servers:
          - url: "http://backend:8080"

  middlewares:
    my_middleware:
      rateLimit:
        average: 100
```

### Provider-System

Traefik unterstützt mehrere Provider für Service Discovery:

**Docker**:
```yaml
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
```

**Kubernetes**:
```yaml
providers:
  kubernetesIngress:
    ingressClass: traefik
```

**File**:
```yaml
providers:
  file:
    filename: /etc/traefik/dynamic-config.yml
    watch: true
```

**Consul**:
```yaml
providers:
  consul:
    endpoints:
      - "http://consul:8500"
```

### Dashboard

Traefik bietet ein Echtzeit-Dashboard:

```yaml
# traefik.yml
api:
  dashboard: true
  insecure: true  # Nur für Development!
```

```bash
# Dashboard öffnen
open http://localhost:8080/dashboard/

# Features:
# - Routers overview
# - Services overview
# - Middlewares overview
# - Health checks status
# - Metrics (requests/s, errors)
```

### Middleware Chains

Traefik ermöglicht Middleware-Verkettung:

```yaml
http:
  routers:
    my_router:
      middlewares:
        - auth
        - ratelimit
        - cors
        - headers

  middlewares:
    auth:
      basicAuth: {...}
    ratelimit:
      rateLimit: {...}
    cors:
      headers: {...}
    headers:
      headers: {...}
```

### Let's Encrypt Integration

Traefik bietet automatische HTTPS-Zertifikate:

```yaml
# traefik.yml
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

# Dynamic config
http:
  routers:
    my_router:
      rule: "Host(`example.com`)"
      entryPoints:
        - websecure
      tls:
        certResolver: letsencrypt
```

### Metrics & Observability

Traefik unterstützt Prometheus, Datadog, StatsD, etc.:

```yaml
# traefik.yml
metrics:
  prometheus:
    entryPoint: metrics
    addEntryPointsLabels: true
    addServicesLabels: true

entryPoints:
  metrics:
    address: ":8082"
```

```bash
# Metrics abrufen
curl http://localhost:8082/metrics
```

---

## Best Practices

### 1. Verwende File Provider für GAL-Generated Configs

```yaml
# traefik.yml
providers:
  file:
    filename: /etc/traefik/dynamic-config.yml
    watch: true  # Auto-reload bei Änderungen
```

### 2. Aktiviere Health Checks für Production

```yaml
services:
  - name: api_service
    upstream:
      health_check:
        active:
          enabled: true
          path: /health
          interval: 10s
```

### 3. Nutze Middleware Chains für komplexe Logik

```yaml
http:
  routers:
    api_router:
      middlewares:
        - auth          # 1. Authentication
        - ratelimit     # 2. Rate limiting
        - cors          # 3. CORS
        - circuitbreaker  # 4. Circuit breaker
```

### 4. Konfiguriere Timeouts für alle Routes

```yaml
routes:
  - path_prefix: /api
    timeout:
      connect: 5s
      read: 30s
      idle: 300s
```

### 5. Verwende Let's Encrypt für automatisches HTTPS

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /letsencrypt/acme.json
      tlsChallenge: {}
```

### 6. Aktiviere Dashboard für Monitoring

```yaml
api:
  dashboard: true
  insecure: false  # Production: Verwende BasicAuth!
```

### 7. Nutze Retry für resiliente Services

```yaml
routes:
  - path_prefix: /api
    retry:
      enabled: true
      attempts: 3
      base_interval: 100ms
```

---

## Troubleshooting

### Problem 1: "No matching router found"

**Symptom**: 404 Not Found, obwohl Service existiert

**Lösung**:
```bash
# Prüfe Router-Regel
http:
  routers:
    my_router:
      rule: "PathPrefix(`/api`)"  # Achte auf Backticks!

# Traefik Logs prüfen
docker logs traefik | grep "my_router"

# Dashboard prüfen
open http://localhost:8080/dashboard/
```

### Problem 2: Health Checks schlagen fehl

**Symptom**: Backend-Server werden als unhealthy markiert

**Lösung**:
```bash
# Prüfe Health Check Endpunkt
curl http://backend:8080/health

# Erweitere Timeout
services:
  my_service:
    loadBalancer:
      healthCheck:
        timeout: 10s  # Erhöhen

# Traefik Logs prüfen
docker logs traefik | grep healthcheck
```

### Problem 3: Middleware wird nicht angewendet

**Symptom**: Rate Limiting/Auth funktioniert nicht

**Lösung**:
```bash
# Prüfe Middleware-Definition
http:
  middlewares:
    my_ratelimit:
      rateLimit:
        average: 100

# Prüfe Router-Middleware-Zuordnung
http:
  routers:
    my_router:
      middlewares:
        - my_ratelimit  # Muss exakt übereinstimmen!

# Dashboard prüfen
open http://localhost:8080/dashboard/
```

### Problem 4: Let's Encrypt Zertifikatsfehler

**Symptom**: HTTPS funktioniert nicht, Zertifikatsfehler

**Lösung**:
```bash
# Prüfe acme.json Berechtigungen
chmod 600 /letsencrypt/acme.json

# Prüfe Email und Domain
certificatesResolvers:
  letsencrypt:
    acme:
      email: valid@example.com  # Muss gültig sein!
      storage: /letsencrypt/acme.json

# Staging Environment für Tests
certificatesResolvers:
  letsencrypt:
    acme:
      caServer: "https://acme-staging-v02.api.letsencrypt.org/directory"

# Logs prüfen
docker logs traefik | grep acme
```

### Problem 5: File Provider lädt Änderungen nicht

**Symptom**: Änderungen in dynamic-config.yml werden nicht übernommen

**Lösung**:
```bash
# Prüfe watch: true
providers:
  file:
    filename: /etc/traefik/dynamic-config.yml
    watch: true  # Muss aktiviert sein!

# Prüfe Volume-Mount
docker run ... -v $(pwd)/dynamic-config.yml:/etc/traefik/dynamic-config.yml

# Manuelle Aktualisierung
docker exec traefik kill -USR1 1

# Logs prüfen
docker logs traefik | grep "Configuration loaded"
```

### Problem 6: Hohe Latenz

**Symptom**: Requests dauern ungewöhnlich lange

**Lösung**:
```bash
# Aktiviere Metrics
metrics:
  prometheus: {}

# Prüfe Metrics
curl http://localhost:8082/metrics | grep traefik_service

# Deaktiviere unnötige Middlewares
# Erhöhe Timeouts
serversTransports:
  default:
    forwardingTimeouts:
      dialTimeout: 10s
      responseHeaderTimeout: 30s

# Nutze Connection Pooling
serversTransports:
  default:
    maxIdleConnsPerHost: 200
```

---

## Zusammenfassung

### Traefik mit GAL

GAL macht Traefik-Konfiguration einfach und provider-agnostisch:

**Vorteile**:
- ✅ **Einheitliche Konfiguration**: YAML statt multiple Provider
- ✅ **Provider-Wechsel**: Von Traefik zu Envoy/Kong in Minuten
- ✅ **Feature-Abstraktion**: Keine Traefik-spezifischen Middlewares im Config
- ✅ **Validierung**: Frühzeitige Fehlerkennung vor Deployment
- ✅ **Multi-Provider**: Parallel Configs für mehrere Gateways

**Traefik-Features unterstützt**:
- Load Balancing (mit Sticky Sessions)
- Active Health Checks
- Rate Limiting (rateLimit Middleware)
- Basic Authentication
- CORS (headers Middleware)
- Timeout & Retry
- Circuit Breaker
- WebSocket (native)
- Header Manipulation
- ⚠️ Body Transformation (nicht nativ, Workarounds verfügbar)

**Best Use Cases für Traefik**:
1. **Docker/Kubernetes**: Automatische Service Discovery
2. **Let's Encrypt**: Automatisches HTTPS erforderlich
3. **Cloud-Native Microservices**: Container-basierte Architekturen
4. **Einfache Konfiguration**: Schnelles Setup bevorzugt
5. **Dashboard-Driven**: Echtzeit-Monitoring erforderlich

**Workflow**:
```bash
# 1. GAL-Konfiguration schreiben
vim config.yaml

# 2. Traefik Dynamic Config generieren
gal generate --config config.yaml --provider traefik --output traefik-dynamic.yml

# 3. Traefik starten mit File Provider
docker run -d \
  -v $(pwd)/traefik-dynamic.yml:/etc/traefik/dynamic-config.yml \
  -v $(pwd)/traefik.yml:/etc/traefik/traefik.yml \
  traefik:latest

# 4. Testen
curl http://localhost:80/api

# 5. Dashboard öffnen
open http://localhost:8080/dashboard/
```

**Links**:
- Traefik Website: https://traefik.io/
- GitHub: https://github.com/traefik/traefik
- Docs: https://doc.traefik.io/traefik/
- Plugins: https://plugins.traefik.io/

---

**Navigation**:
- [← Zurück zur Übersicht](README.md)
- [Envoy Provider Guide](ENVOY.md)
- [Kong Provider Guide](KONG.md)
- [APISIX Provider Guide](APISIX.md)
- [Nginx Provider Guide](NGINX.md)
- [HAProxy Provider Guide](HAPROXY.md)
