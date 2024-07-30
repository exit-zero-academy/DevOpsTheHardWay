# Milestone: Simple app deployment

For this milestone, you will manually deploy the [NetflixMovieCatalog][NetflixMovieCatalog] service on an AWS virtual machine.

1. In an AWS account, create an EC2 instance.
2. Run the NetflixMovieCatalog within your instance as a Linux service[^1] that starts automatically when the instance is starting. Create Python venv and install dependencies if needed. 
3. In Route 53, configure a subdomain in the hosted zone of your domain to route traffic your instance IP.
   Access the service domain via your browser and make sure it's accessible.  
4. Now, configure your Flask application to accept only HTTPS traffic by generating a self-signed certificate. Update the Flask app code to use the certificate, as follows:

   ```diff
   - app.run(port=8080, host='0.0.0.0')
   + app.run(port=8080, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
   ```
   
   While `cert.pem` and `key.pem` are paths to your generated certificate and private key. 
5. Visit your service via your browser using the HTTPS protocol. 


[NetflixMovieCatalog]: https://github.com/exit-zero-academy/NetflixMovieCatalog.git

[^1]: Linux services discussed [here](linux_processes.md#services)