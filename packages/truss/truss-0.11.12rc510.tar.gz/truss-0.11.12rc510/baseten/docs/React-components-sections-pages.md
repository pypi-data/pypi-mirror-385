# React components sections pages

In usual `React` applications we can notice such kind of structure:

```bash
/components
/sections
/pages
/routes
/store
/theme
/config
/utils
```

They can be more or less based on the particular project, but now let's concentrate on the three of them `/components`, `/sections`, `/pages`. Let's understand how we define these concepts and let's make a step-by-step guideline to help newcomers to create a new `/component`, `/section`, or `/page`.

Let's consider the following example, the `Home` page; here how it looks:

<img width="1680" alt="Screen Shot 2021-07-12 at 12 52 12" src="https://user-images.githubusercontent.com/13118722/125262312-2172fd80-e313-11eb-9be4-64a3865fba2e.png">

#### Pages

We call `Home` a page. *Page is a piece of the application that usually has a root route*, like `/home`, `/applications`, `/models`, etc. In the routes file, we define which page will be rendered in the particular route:

<img width="1002" alt="Screen Shot 2021-07-12 at 13 20 58" src="https://user-images.githubusercontent.com/13118722/125263404-0a80db00-e314-11eb-96e0-da90c2084916.png">

Usually, we load them asynchronously - our application can have many pages, and each page can use specific libraries, packages, utilities, modules, services, etc, to avoid having a single huge bundle, we make smaller chunks for each page, and provide only that chunk which the user needs right now - it makes our application faster and more user friendly.

There is a root folder called `/pages`, where we have page-name folders with all page-related things inside.

```bash
/components
/sections
/pages
  - /Home
  - /Applications
  - /Models
  - /DataSources
  - ...
```

#### Sectionis

A page consists of sections. *Sections are self-sufficient pieces of the application that contain an application-specific logic*. Our `Home` page consists of many sections, like `Search`, `Welcome`, `Applications`, `Models`, `GettingStarted`, `OtherActions`, etc.

![photo_2021-07-12 14 22 11](https://user-images.githubusercontent.com/13118722/125272161-972f9700-e31c-11eb-931c-2e10e1c90b45.jpeg)

Sections can be found inside the particular page, like this:

<img width="196" alt="Screen Shot 2021-07-12 at 14 24 42" src="https://user-images.githubusercontent.com/13118722/125272457-ed9cd580-e31c-11eb-8d2b-580cd9ebc30e.png">

as well as inside the root `/sections` folder. If you find that this very section can be used in other pages, it can be easily moved to the root sections folder. In any case, in the beginning, they should be designed in a way to be independent and self-sufficient. For example, let's consider the `Welcome` section of the `Home` page:

<img width="1680" alt="Screen Shot 2021-07-12 at 14 28 15" src="https://user-images.githubusercontent.com/13118722/125273143-ac58f580-e31d-11eb-9805-2e839ac57eba.png">

It says hello to the current user, here is the file/folder structure of the `Welcome` section:

<img width="300" alt="Screen Shot 2021-07-12 at 14 31 24" src="https://user-images.githubusercontent.com/13118722/125273358-e32f0b80-e31d-11eb-8af3-173ee977af07.png">

and the actual `Welcome.tsx` component:

<img width="917" alt="Screen Shot 2021-07-12 at 14 34 37" src="https://user-images.githubusercontent.com/13118722/125273758-4faa0a80-e31e-11eb-92dd-98babb8a56c0.png">

If we think it can be used on other pages, we can move it to the root sections folder, without any problems.

#### Components

`Components` are the reusable pieces of our applications; the building blocks that can be used everywhere, like:

```bash
/components
 - Button/
 - Input/
 - Tag/
 - Typeography/
 - Divider/
 ...
```

Usually, we use a UI framework, like [Material-UI](https://material-ui.com/), [Chakra UI](https://chakra-ui.com/), [Ant Design](https://ant.design/), [Blueprint.js](https://blueprintjs.com/), etc, that provides us the necessary component set. However, usually, we have project-specific components, or we have a need to modify a default behavior or design elements. So, all this happens in the root `/components` folder.

<hr />

#### Predictable and simple JSX

The other thing related to the pages/sections/components and their relationships that should be mentioned is that usually, the render methods should represent what we see on the screen in a predictable way. Let's consider the main, `Home.tsx` file of the `Home` page.

<img width="461" alt="Screen Shot 2021-07-12 at 14 41 02" src="https://user-images.githubusercontent.com/13118722/125274627-335a9d80-e31f-11eb-9e1a-2528e2e2e959.png">

Here we can notice that in addition to some modals, the `Home` page consists of the `Search` section, and the rest that we called `Content`, here is the `Content`:

<img width="720" alt="Screen Shot 2021-07-12 at 14 44 07" src="https://user-images.githubusercontent.com/13118722/125275071-a2d08d00-e31f-11eb-9d07-3f3c2aaec1ae.png">

Basically, what we see on the screen is projected here, almost in the same way.

Now, let's see the `Search` section:

<img width="701" alt="Screen Shot 2021-07-12 at 15 10 41" src="https://user-images.githubusercontent.com/13118722/125278270-8cc4cb80-e323-11eb-9ee8-70f1ac941906.png">

We can notice that the `Search` section consists of an input and popover for search results. The important part here is that, at first, we stress only the high-level concepts in this context - you can notice the `<New />` and `<Results />` components are extracted making our `JSX` much simpler and readable. Here is the `<New />` component:

<img width="419" alt="Screen Shot 2021-07-12 at 15 17 35" src="https://user-images.githubusercontent.com/13118722/125278898-5471bd00-e324-11eb-86bb-993b93e232d7.png">

and here is the `<Results />` component:

<img width="734" alt="Screen Shot 2021-07-12 at 15 18 26" src="https://user-images.githubusercontent.com/13118722/125278978-6d7a6e00-e324-11eb-8cf8-b6bdebcd5bab.png">

<img width="317" alt="Screen Shot 2021-07-12 at 15 19 05" src="https://user-images.githubusercontent.com/13118722/125279079-8c790000-e324-11eb-9e33-1a7ebfb539e3.png">

This simplistic and predictable design helps us to find things faster, keep things simple, be able to encapsulate the logic, and make parts of the application highly testable.




