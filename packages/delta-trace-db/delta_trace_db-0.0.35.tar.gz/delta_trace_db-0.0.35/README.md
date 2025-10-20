# delta-trace-db

Python implementation of DeltaTraceDB.

## Usage

Here's a simple example of server-side code:  
[ServerSide Example](https://github.com/MasahideMori-SimpleAppli/delta_trace_db_py_server_example)  

If you want to construct queries directly, please refer to the [Dart version](https://github.com/MasahideMori-SimpleAppli/delta_trace_db).  
There are some differences, such as arguments and functions being in snake case,  
and an underscore being added after the variable name if the namespace conflicts with a standard function,  
but the usage is the same.

I am also developing an open source editor for manually editing the DB contents:  
[DeltaTraceStudio](https://github.com/MasahideMori-SimpleAppli/delta_trace_studio)  

## Speed

This package is an in-memory database, so it is generally fast.  
Currently, there is no mechanism to speed it up, but it works almost the same as a for loop in a program,  
so there is usually no problem with around 100,000 records.  
I recommend that you test it in an actual environment using test_speed.py in the test folder.  
However, since it consumes RAM capacity according to the amount of data,  
if you need an extremely large database, consider using a general database.  
For reference, below are the results of a speed test (tests/test_speed.py) run on a slightly  
older PC equipped with a Ryzen 3600 CPU.  
The test conditions were chosen to take a sufficiently long time, but I think it will rarely
cause   
any problems in practical use.
Please note that speeds also depend on the amount of data, so if you have a lot of large data, it will be slower.

```text
tests/test_speed.py speed test for 100000 records
start add
end add: 342 ms
start getAll (with object convert)
end getAll: 663 ms
returnsLength: 100000
start save (with json string convert)
end save: 469 ms
start load (with json string convert)
end load: 561 ms
start search (with object convert)
end search: 868 ms
returnsLength: 100000
start search paging, half limit pre search (with object convert)
end search paging: 424 ms
returnsLength: 50000
start searchOne, the last index object search (with object convert)
end searchOne: 39 ms
returnsLength: 1
start update at half index and last index object
end update: 90 ms
start updateOne of half index object
end updateOne: 16 ms
start conformToTemplate
end conformToTemplate: 81 ms
start delete half object (with object convert)
end delete: 628 ms
returnsLength: 50000
start deleteOne for last object (with object convert)
end deleteOne: 22 ms
returnsLength: 1
start add with serialKey
end add with serialKey: 99 ms
addedCount:100000
```

## Future plans

It is possible to speed up the database, but this is a low priority, so I think that improving
usability and creating peripheral tools will take priority.

## Notes

This package is primarily designed for single-threaded operation.  
Unlike the Dart version, most methods within the DeltaTraceDatabase class acquire an RLock and can be called in
multi-threaded mode, but other classes and utility functions are not thread-safe, 
so care must be taken when using them in parallel.
Additionally, for parallel processing that does not share memory (e.g., across processes), message passing or similar 
mechanisms are required, just like in the Dart version.  


## Support

There is essentially no support at this time, but bugs will likely be fixed.  
If you find any issues, please open an issue on GitHub.

## About version control

The C part will be changed at the time of version upgrade.  
However, versions less than 1.0.0 may change the file structure regardless of the following rules.

- Changes such as adding variables, structure change that cause problems when reading previous
  files.
    - C.X.X
- Adding methods, etc.
    - X.C.X
- Minor changes and bug fixes.
    - X.X.C

## License

This software is released under the Apache-2.0 License, see LICENSE file.

Copyright 2025 Masahide Mori

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Trademarks

- “Dart” and “Flutter” are trademarks of Google LLC.  
  *This package is not developed or endorsed by Google LLC.*

- “Python” is a trademark of the Python Software Foundation.  
  *This package is not affiliated with the Python Software Foundation.*

- GitHub and the GitHub logo are trademarks of GitHub, Inc.  
  *This package is not affiliated with GitHub, Inc.*
