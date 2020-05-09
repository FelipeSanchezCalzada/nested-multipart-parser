# Multipart Form Data for Django Rest Framework

This parser accepts the format returned by the library [object-to-formdata](https://github.com/therealparmesh/object-to-formdata) available for javascript.

Needs the following config in object-to-formdata:
```
{
    indices: true,
    nullsAsUndefineds: false,
    booleansAsIntegers: false
}
```
