# Add a new transactional email

To add a new transactional email, you need to follow these steps:

1. Create a new email template in `Loops`.
2. In `EmailEmitter`, add a new method that sends the email using the new template.

## Create a new email template

1. Go to the `Loops`'s [transactional page](https://app.loops.so/transactional) and create a new email template. You can use the existing templates as a reference.

2. While creating the template, you can use variables (called `data variables`) to personalize the email content.

3. Once you have created the template, go to publish section. Here you can see the `transactional id` (the unique identifier of the template) and the list of `data variables` that you can use in the email.

4. Finally, publish the template to make it available for use.

## Add a new method in EmailEmitter

1. Go to the [EmailEmitter](../../backend/common/utils/email_emitter.py) file.

2. Add a new method that sends the email using the new template. You can use the existing methods as a reference.

So, that's it! You have successfully added a new transactional email. 🎉

Now, you can use `EmailEmitter.new_method(...)` to send the email using the new template.
