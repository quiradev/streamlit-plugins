# Multilit (Inherit from Hydralit)
This is a fork of [Hydralit](https://github.com/TangleSpace/hydralit).

In this version, I update all the code to be compatible with the last version of streamlit.
And it improves the interface to be more user-friendly. Also, it respects the strealit active theme and can be override by the user.
In a future is planned to incorporate the new multipage native of streamlit. Instead of the current implementation.

Can use built-in buttons to change the page, or use a function to change the page programmatically.
![Change Page with button](https://raw.githubusercontent.com/quiradev/streamlit-plugins/main/resources/demo2.gif)

You can install extra components to work with multilit framework.
```bash
pip install streamlit-framework-multilit[navbar,loader]
```