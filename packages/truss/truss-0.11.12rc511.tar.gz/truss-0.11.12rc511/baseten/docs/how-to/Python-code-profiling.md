# Python Code Profiling

line_profiler is a module to profile python code line by line.
Install:

```sh
pip install line_profiler
```

In ipython environment:

```python
%load_ext line_profiler
```

Say you have functions `foo` and `bar` you'd like to profile, where `foo` calls `bar`:

```python
%lprun -f foo -f bar foo(x)
```

will generate a report like the following:

```text
Timer unit: 1e-06 s

Total time: 4e-06 s
File: <ipython-input-3-d520e5efb693>
Function: bar at line 1

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     1                                           def bar(x):
     2        10          4.0      0.4    100.0      return x + 1

Total time: 2e-05 s
File: <ipython-input-5-edcd7f4ce017>
Function: foo at line 1

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     1                                           def foo(x):
     2         1         20.0     20.0    100.0      return [bar(x) for _ in range(10)]
```
