This starter template combines FastAPI (for the web server) and SendGrid (for user verification email), and is deployable on Deta (www.deta.sh).

# External dependencies

Before you get to the nitty gritty, go ahead and create an accound on deta.sh.
Create a project and take note of the project secret key, you'll need it to configure the template to run locally on your machine.

Now go ahead and create a Sendgrid account. Sendgrid has a free tier plan that can be used in the beginning of a project. Frankly, it's been awhile since I went through this process of creating a account and obtained an API key, but that's your goal here: obtain an API key from Sendgrid. Take note of that one too!

PS: at the time of writing, folks at Deta have not yet implemeted their `send_email` functionality, but there is a plan to do so. For now, sendgrid is the weapon of choice.

# Getting started

This template was created and tested using Python 3.9.5

```bash
gh repo clone regisin/template-fastapi-deta my-app

cd my-app
```

Now it's time to configure those API keys. This template has a `sample.env` file. Go ahead and rename it to `.env`, we'll do ourselves a favor and just edit the template. Change the variables according to your app. Here's a breakdown of what they are:

| Variable    | Description |
| ----------- | ----------- |
| NO_REPLY_EMAIL      | The `from` email address that new users will receive in their inbox. Need to verify on Sendgrid's end to work   |
| APP_NAME            | The name of your app, used in the documentation and emails                                                      |
| SENDGRID_API_KEY    | The API key obtained from Sendgrid                                                                              |
| DETA_KEY            | The secret key to your deta project, needed to interact with deta.sh. Only needed if you run the app locally    |
| DETA_ID             | The project ID, from deta. Only needed if running locally                                                       |
| SECRET_KEY          | A secred string used by FastAPI to encrypt passwords. You can generate a random one with `openssl rand -hex 32` |
| ALGORITHM           | Default: `HS256`. The algorithm used for encryption. No need to change unless you know what you are doing       |
| ACCESS_TOKEN_EXPIRE_MINUTES | Default: `30`. Time in minutes that auth tokens are valid for                                           |

# Run locally

If you want to run your FastAPI app locally, then create a virtual enviroment and install the requirements.

```bash
cd my-app

python3.9.5 -m venv env
source env/bin/active

pip install -r local_requirements.txt
```

It's unorthodox to use a requirements file that's not `requirements.txt`, but we do that here because if you choose to deploy on deta later, you will want to minimize the requirements (deta uses `requirements.txt` out of the box). Deta micros come with some of the packages readily available, so we don't have to tell it to install it. It will save some space in the deta micro (which has a 200mb limit).

After installi g the requirements you can run the app:

```bash
cd my-app

uvicorn app.main:app --reload
```

You can now navigate to `http://localhost:8000/api/v1/docs`.

# Deploy on Deta

Remember that the requirements for locl deployment were a little different than when you deploy to Deta? Well, rename the file `deta_requirements.txt` to `requirements.txt`. This way once you deploy to Deta, it will pick up the correct requirements!

Both `deta_` and `local_` requirement files are provided here just to make it obvious the differences. The only difference at the moment being `uvicorn`.

To deploy your API on deta, first install the Deta CLI:
```bash
curl -fsSL https://get.deta.dev/cli.sh | sh
```

Then authenticate your CLI with your deta account:

```bash
deta login
```

Now create a new micro:

```bash
cd my-app

deta new

deta update -e .env
```

If everything goes right, you will see a message similar to this:

```bash
Successfully created a new micro
{
        "name": "my-app",
        "runtime": "python3.7",
        "endpoint": "https://{micro_name}.deta.dev",
        "visor": "enabled",
        "http_auth": "enabled"
}
Adding dependencies...
Collecting fastapi
...
Successfully installed fastapi-0.68.1 ...
```

Take note of the endpoint, that will be your API's base url. Now visit the `https://{micro_name}.deta.dev/api/v1/docs`. You can start test the Sendgrid integration by trying out the `/api/v1/auth/signup` endpoint.

# Limitations

This is just a template and is provided as is. Currently `pytest` testing is not implemented, although the mechanisms are in place for future unit tests.