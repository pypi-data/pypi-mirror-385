# Selectors in view builder code

## What are selectors?
Selector is a function that given an object provides another object, usually a subset of it. 

## Why do we use selectors?
We started using selectors when we adopted Redux. Redux stores the state of the application in it's, well, 'store'. This state is global and is quite huge. Typically in a component we want only a small portion of it, e.g. the state of a worklet. Selector function make it easy to get that part from the global redux state. Redux provides a hook called `useSelector` for supplying a selector function to get subset of state.

In addition to ease of use `useSelector` provides another critical functionality. The react component that uses the `useSelector` hook is re-rendered if the value returned but the selector changes. This provides a mechanism similar to useState and makes sure the component always shows the current value, regardless of how the global state got changed. Second, and very important, the component isn't rendered on any change to the global state, but only if the returned value of the selector changes. This is important because the global state changes quite a lot, almost on every key-stroke or action on the UI and without this mechanism almost everything in the entire application will render every time (note that rendering a parent re-renders all its children as well), which simply won't do.

## What is selector algebra?
We initially started by defining specific selectors for everything we envisioned we'll need but while building the new view builder we realized that we needed to work with selectors at whole another level, that I will explain later. In short, we needed to be able to transform selectors to create other selectors. Selector Algebra is a library of utility functions that help do that.

## Why is it called algebra?
Selectors are really just State Monad. In layman terms a Monad is something that encloses a value and a monad can be transformed by passing it functions that modify the enclosed value. We do this all the time in programming with or without realizing. e.g. `array.map(elem => elem + 1)` is an example of a list monad being transformed with a `+1` method.
Monads are a well defined mathematical concept with full algebra. We could have just used a functional js library and got all these methods, but what I've found is that it makes the code way too abstract to easily read. For now I've defined a subset of that functionality with functions with very descriptive names in `SelectorAlgebra.ts`. The functions don't form a full algebra (it would be pretty easy to do so though) but I feel it's still a good name for it.

## Why do we need Selector Algebra for new ViewBuilder?
The new View Builder is built around composability, essentially having a powerful component concept that can contain other components to form a composite tree. Each component has a clean contract, part of which is around sharing state with other components.

Essentially, a component can share data with its parent and only its parent (the parent can decide to share it further but it has to do that explicitly). Sharing data with parent allows the parent to pass stuff around between it's children and thus allow data dependencies, e.g. showing what's typed in a TextInput in a TextDisplay. Restricting to parent only is to avoid deep dependencies, a component should only depend on what it directly touches it's children and not anything internally used by the children, otherwise it breaks modularity, changes to the api of a component can require changing whole lot of stuff.

Now, while parent component has access to children's state it doesn't mean that it uses them. It may not use them at all or use parts of them. So a parent shouldn't re-render when any of its children's state changes, it should re-render only when something it cares about changes. This fits very well with the selector mechanism above. The parent component uses selectors for everything it needs (which is mostly around resolving value of user code snippets). It turns out there is a lot of selector manipulation required for achieving this and selector algebra comes in really handy.

## Crash course on Selector and Selector Algebra
A selector is just a function that produces one value from another.
```
type Selector<S, T> = (state: S) => T;
```

The simplest thing you can possibly do is create another selector out of it by passing it a function. That's what mapSelector is for.
```
function mapSelector<S, T, U>(selector: Selector<S, T>, fn: (t: T) => U): Selector<S, U>
```
That's a mouthful but let's say the state were fixed (it's not, but just to understand this better)
``` 
function mapSelector<T, U>(selector: Selector<T>, fn: (t: T) => U): Selector<U>
```
It's basically the signature of map method in lodash, expect that it works with Selectors instead of collections.

Another thing you may want to do is combine selectors e.g. with `combineSelectorsPair`, which given two selectors produces the selectors that produces a pair of the value returned by the two.
Or with combineSelectorsArray that does the same for an array.
Or with combineSelectorsRecord that does the same for a ts record, which is just the js object.

In practice when you combine selectors you typically want to do something with the combined value, instead of chaining mapSelector you can use helper functions such as `mapSelectorPair` that do both.

You may also chain selectors in way that you want to select something and then select something else out of the return value. You can do this with `thenSelector`. `thenSelector` is really useful in redux, where we have a tree of things and we may have one selector provide part of the tree and then another to select something from the subtree.

## Conclusion
While it's much easier just to manipulate something rather than manipulate a Selector that will provide you that, there are reasons outlined above that force this indirection.

Do note that it's not that bad, you don't have to use selector algebra. You can always just do 
```
(state) => {
  // Here you have access to state like if it were available.
}
```
Selector Algebra reads nicer most of the time, but it takes getting used to and sometimes the above may style may actually be clearer. Use your judgment.

