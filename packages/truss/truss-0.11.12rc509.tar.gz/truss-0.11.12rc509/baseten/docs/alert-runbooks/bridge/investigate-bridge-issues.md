# Investigating Bridge Issues
This runbook lists common places and components to investigate when alerted for a bridge issue

### Resource 
* Grafana (loki logs and victoria Metrics): https://grafana.baseten.co/d/bb483619-afc7-4672-9d53-9f21b1d2cb8b/bridge-dashboard?orgId=1 

### 1 - Quantify/Qualify the Impact
- If there isn't a specific customer, start by looking at the grafana for respective error rates. Identify the route it's coming from. Some routes have a Model ID in the URL. If that's the case use the Model ID as a starting place
- If there's a specific customer: 
  - Understand what the symptoms of the incident are (i.e. success rate, error responses, etc.)
  - If the customer has the Model ID or Deployment ID, that's great. If not, try to find it in the logs in the URL

### 2 - Reproduce Locally
- See the [README](https://github.com/basetenlabs/baseten/tree/master/openai-proxy) for running the code locally. By default, any instance of the bridge will hit production models. You should not need to deploy models into any environment that isn't production

### 3 - Deploy fix 
- See the [README](https://github.com/basetenlabs/baseten/tree/master/openai-proxy) for instructions on deploying the bridge
