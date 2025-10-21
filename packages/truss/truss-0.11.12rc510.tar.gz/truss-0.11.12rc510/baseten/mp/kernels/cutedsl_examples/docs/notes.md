# Typical cute implementation flow

Let's take `cute.elem_less`

- Defined in core.py it calls `_cute_ir.elem_less`
- Which uses `ElemLessOp`
- The operation has an operation name `cute.elem_less` and a bunch of operands
- `cute.elem_less` is implemented on the C++ side in `int_tuple.hpp`
```cpp
// Shortened
elem_less(IntTupleA const& a, IntTupleB const& b) {
  if constexpr (is_tuple<IntTupleA>::value && is_tuple<IntTupleB>::value) {
    return detail::elem_less_impl<0>(a, b);
  } else {
    return a < b;
  }
}

elem_less_impl(TupleA const& a, TupleB const& b) {
// Shortened
  if constexpr (I == tuple_size<TupleA>::value) {
    return cute::true_type{};     // Terminal: TupleA is exhausted
  } else if constexpr (I == tuple_size<TupleB>::value) {
    return cute::false_type{};    // Terminal: TupleA is not exhausted, TupleB is exhausted
  } else {
    return elem_less(get<I>(a), get<I>(b)) && elem_less_impl<I+1>(a,b);
  }
}
```

This is a general pattern:
- A cute function is typically a wrapper over `_cute_ir` function, which creates
  an `Op`, which ultimately implements the operation in C++
- The way to walk the code is to do the above then look at the implementation in C++