# Email Bot

Have you ever had issues managing your emails ? Finding the email you are looking for amongst thousands of emails ?
Managing your inbox ? Or having too many emails you do not know from where to start ?

This project goal is to solve these problems. Using the capacity of LLMs, you will have access to a chatbot
that will help you manage your emails. One important point: it is fully working locally, no cloud. The benefit:
your emails are not outsourced, and you keep your privacy !

For the moment, the application is able to handle gmail mailbox, but plans to handle other services are
in the backlog.

**NB**: currently works on MacOS users, will be adapted for Windows users ASAP.

## Setting up the project

### 1. Create environment

Run the command :

`make environment`

This will install all the dependencies needed to run the application


### 2. Credentials to connect to GMail

The application uses the GMail API, using a token. You can get it from the [Google APIs' dashboard](https://console.developers.google.com/apis/dashboard)

1. First enable the Google mail API, head to the dashboard, and use the search bar to search for Gmail API, click on it, and then enable
2. Create an OAuth 2.0 client ID by creating credentials (by heading to the Create Credentials button)
3. Click on Create Credentials, and then choose OAuth client ID from the dropdown menu
4. Select Desktop App as the Application type and proceed
5. Go ahead and click on DOWNLOAD JSON; it will download a long-named JSON file. Rename it to `credentials.json` and put it in the `credentials` folder


### 3. LLM and configuration

The general configuration can be found in the `config.yaml` file. Currently, the project handles `.llamafile`
to work locally. The default model is `Phi-3-mini-4k-instruct.Q4_K_M.llamafile` but feel free to go on
HuggingFace and take another model (for example Phi 3 with a bigger context, depending on your infrastructure)

The other parameters are free for the user to modify.


### 4. Run the app

To run the app, open a terminal and run `streamlit run streamlit_app.py`.

The first time, it will take some time as the application needs to build the RAG for the emails. Next time,
you just need to wait for the `.llamafile` to finish loading.
