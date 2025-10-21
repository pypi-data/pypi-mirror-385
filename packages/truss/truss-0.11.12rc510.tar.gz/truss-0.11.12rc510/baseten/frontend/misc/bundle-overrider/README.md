# Bundle overrider

The bundle overrider is a Chrome extension that allows you override the cloud-deployed Baseten application, injecting frontend changes from your local webpack server. This enables your to test front-end changes against cluster environments with only a webpack server, no need for django or a minikube cluster.

[Loom demo](https://www.loom.com/share/03914addc0c54c54ad8b050a764dee01)

## Uses

- Validating changes, like targeted bug fixes, in cluster environments that are hard to reproduce locally
- Better debugging of issues in cluster environments through the use of better sourcemaps, support for React and Apollo devtools, and the ability to add logging

## Getting started

Start your webpack server normally:

```sh
npm run start
```

Wait for the webpack compilation to finish before continuing.

Next, install this extension as an unpacked extension. Follow the instructions [here](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked), pointing to this directory (`misc/bundle-overrider`). You may need to clone the Baseten repo locally to do this.

The extension should show up in Chrome like this:

![Extension loaded in Chrome](assets/extension.png)

Next to the address bar, you should see the extension icon. It should look like this:

![Extension popup](assets/popup.png)

The checkbox indicates whether the extension is enabled or not. By default, it is disabled.

Finally, navigate to the [Baseten application](https://app.baseten.co/). You can use either dev, staging, or production.

You should see your local changes in then frontend.

To go back to the real, deployed frontend, simply disable the extension in Chrome. You only need to install the extension once.

## How it works

The webpack dev server is configured to expose [chunks.json](http://localhost:3000/chunks.json). This contains a mapping of the webpack chunks included by every entrypoint. See [webpack.local.config.js](../../webpack.local.config.js) for more info.

When you load the Baseten application, the extension does the following:

- Using the [declarativeNetRequest](https://developer.chrome.com/docs/extensions/reference/api/declarativeNetRequest) API:
  - It blocks the real CDN-backed JavaScript bundles
  - It removes the Baseten app's `Content-Security-Policy` response header, which otherwise blocks local requests from loading
- It uses a [content script](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts) to fetch `chunks.json` from the webpack dev server. It then loads each main chunk script onto page.

## Limitations and gotchyas

- No support for live reload. You'll need to refresh the page manually after making changes.
- Only frontend changes can be tested with this approach.
- This workflow is prone to API compatibility breaks (e.g. mismatch in the GraphQL schema between client and server), especially when your branch's baseline commit differs significantly from what's running on the cluster environment.
