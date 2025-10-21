# How to create orgs locally

## Requirements
You will need a working local setup

## Steps
1. Start the app (backend and frontend)
2. Go to the login page (http://localhost:8000)
3. Create a new account by signing up with email. The email doesn't matter as it will not be sent
4. This will open a tab in your default browser with a signup link. Visit that link
5. You will need to manually approve this user.
    1. In an incognito window, login with the admin user (baseten/baseten)
    2. Navigate to the admin panel (http://localhost:8000/billip)
    3. Go the the user page
    4. Select the user you created at step 3, select the "Approve user and provision organization resources" in the action dropdown and click "Go"
        * This can take a while if it needs to build a docker image for the pynode
6. Once the user is approve, another browser tab will open where you will be asked to complete your profile. Do it!
7. Enjoy your new organization
