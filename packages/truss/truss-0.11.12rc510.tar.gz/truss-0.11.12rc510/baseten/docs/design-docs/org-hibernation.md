# Hibernating Organizations
We've implemented various forms of hibernating unused and inactive organizations over the years. Consider this the most up to date version of "hibernation"

## When do organizations get hibernated?
**After two weeks of inactivity**, an organization is eligible for hibernation. _An organization gets sent a warning email 48 hours before hibernation if it has models eligible for hibernation._

### How is an organization eligible for hibernation?
* No models have been accessed for the hibernation period.
* No activity has been recorded on the organization for the hibernation period.


Activity is measured by the following:
* User logs in
* User interacts with an application in a meaningful way (invokes worklet, opens console, publishes application)
* User interacts with data in a meaningful way (creates/edits UDM, external connections or queries, runs queries)
* User creates or edits secrets
* User deploys/promotes/activates a model
* Having a model in an active state (ready, building, loading, deploying, updating, unhealthy, etc)
* User invokes model via curl (also via `truss predict`` but this is less accurate)

## What does hibernation do?
* Hibernation will delete all knative services associated with org-level and workflow-level pynodes. 
* All models will be deactivated. 
* The organization's kubernetes namespace will be deleted.

## Which organizations are hibernated by default?
**By default, all organizations not on the Pro tier can be hibernated**. 

## Which organizations' pynodes are scaled to zero by default?
**All organizations on all tiers also have their pynodes scale to zero after an hour by default.** This setting can be changed on a per-organization and per-workflow basis. See the section below.

## How can I change an organization's hibernation and scaling settings?

### To change whether an organization can hibernate
In the [billip Licenses page](https://app.baseten.co/billip/users/license/), do the following:

Select an organization and toggle its license customizability
![image](https://github.com/basetenlabs/baseten/assets/20553087/d93fdfe7-5093-420d-8b1a-8cb8c1451c7e)

Then click on its license and update the `enable_org_hibernation` flag accordingly
![image](https://github.com/basetenlabs/baseten/assets/20553087/969da17d-f486-4d68-9c9b-e3f2c2e971eb)


### To change whether an organization's pynodes can scale to zero
In the [billip Organizations page](https://app.baseten.co/billip/users/organization/), select an organization and set the appropriate flag:
![image](https://github.com/basetenlabs/baseten/assets/20553087/8f08de77-cc9e-4404-8675-4111ad41be8a)

### To change whether a workflow's pynodes can scale to zero
In the [billip Workflows page](https://app.baseten.co/billip/workflows/workflow/), select a workflow and set the appropriate flag:
![image](https://github.com/basetenlabs/baseten/assets/20553087/054a0fda-ae36-462b-b830-38d25bfb8c58)
