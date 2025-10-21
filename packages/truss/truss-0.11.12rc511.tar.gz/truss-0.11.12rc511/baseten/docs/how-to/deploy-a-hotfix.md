# Deploying a HotFix
...to Baseten's `production` branch

😱 Broke something in production? Fear not and trust in the hotfix process (assuming you have a fix that you've deployed to staging).

0. Post in [#deployments-production](https://basetenlabs.slack.com/archives/C0363QD4NJX) and [#engineering-discussion](https://basetenlabs.slack.com/archives/C014JUXFGLU) that production is currently broken and that you've identified a fix.

1. Merge a PR for the fix (make sure to **Squash and merge**).

2. Validate that the fix works on staging.

3. Create a hotfix branch on the `production` branch by doing the following:
* checkout the production branch
  ```
  git checkout production
  git pull
  ```

* create a new hotfix branch off of production
  ```
  git checkout -b {your name}/hotfix-{pr number}
  ```


* 🍒 cherrypick the **merge** commit

  Grab the relevant commit hash from here: https://github.com/basetenlabs/baseten/commits/master
  ```
  git cherry-pick <your merge commit SHA>
  ```

* push your commit to your new branch
  ```
  git push origin {your name}/hotfix-{pr number}
  ```
*  open up a PR from your `{your name}/hotfix-{pr number}` branch into `production`

4. Notify the `#deployments-production` Slack channel that your hotfix is about to go out.

5. Merge your hotfix PR to production.

6. Validate that the fix works.

7. Get the `master` branch consistent with `production`.
(A good example pr can be found [here](https://github.com/basetenlabs/baseten/pull/7453))
* make a new branch off of the latest `master`
  ```
  git checkout master
  git pull
  git checkout -b {your-name}/master-prep
  ```
* merge the latest `production` into your `{your-name}/master-prep` branch
  ```
  git merge production
  ```
* resolve changes, **take changes on `master` over what's on `production`**
  ```
  git checkout . --ours
  ```
* create a PR from your `{your-name}/master-prep` branch into `master`
* 🚨 make sure to **Create a merge commit** when merging instead of Squash and merge

  (you'll likely need to _temporarily_ enable this branch protection setting)
  ![image](https://github.com/basetenlabs/baseten/assets/20553087/6604b44e-4a85-4c1c-b39f-4f4f4c1be46e)

8. A very well deserved ice cream 🍦
