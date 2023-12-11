# Streamlit app for colombia-economy website

All packages must be located inside a virtual environment. For doing so, you first need to install virtualenv.

``` pip install virtualenv ```

Then, create a virtual environment.

``` virtualenv ~/streamlit ```

Now, activate such an environment.

``` source ~/streamlit/bin/activate ```

Within it, you can install any needed package using pip. After configuring the environment, you can also export the requirements by executing.

``` pip freeze > requirements.txt ```

If you want to replicate the environment in another machine, you only need to create a new environment as mentioned before and install the specified requirements.

``` pip install -r requirements.txt ```

Finally, you can run the streamlit app.

``` streamlit run demo.py ```

``` streamlit run peso_behavior.py ```
