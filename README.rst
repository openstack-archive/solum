Solum
=====

Solum is a system for simplifying deployment of many types of applications.
You can think of it as being similar to a Platform-as-a-Service (PaaS).

It manages the lifecycle of your application and handles everything from
taking your code to getting it running.

It leverages many existing OpenStack components including the Nova Docker
driver, Heat, Neutron, Glance, and Swift.

It is intented to be a high-density, multi-tenanted service.

It is currently in development and not yet usable.

API
---

* Application Management
 * Create/Read/Update/Delete
  * Create - POST /applications/
  * List - GET /applications/
  * Read - GET /applications/{id}/
  * Update - PUT|PATCH /applications/{id}/
  * Delete - DELETE /applications/{id}/

 * Process Management
  * Set # of containers - PATCH /applications/{id}/processes/{process_name}/


 * Environment
  * Add/change variable - PUT /applications/{id}/environment/{variable_name}/
  * Delete variable - DELETE /applications/{id}/environment/{variable_name}/

 * Logs
  * GET /applications/{id}/log/
  * GET /applications/{id}/processes/{process_name}/log/

 * Versions
  * List versions - GET /applications/{id}/versions/
  * Specific version info - GET /applications/{id}/versions/{version_id}/

 * Deployments
  * List deployments - GET /applications/{id}/deployments/
  * Deploy version - POST /applications/{id}/deployments/

 * TLS Certificate
  * List fingerprints and metadata - GET /applications/{id}/certificates/
  * Add certificate - POST /applications/{id}/certificates/
  * TODO: replace certificate

Representations
---------------

* Application

.. code-block:: json

    {
        "name": "<string>",

        "domains": [
            "<application-name>.solumapp.io",
            "example.com",
            "*.example.com",
        ],

        "metadata": {
            "key": "value"
        }
    }

* Process

.. code-block:: json

    {
        "name": "<string>",
        "command": "<string>",
        "desired_instances": 10
    }

* Environment

.. code-block:: json

    {
        "key": "<string>",
        "another_key": "<string>"
    }

* Version

.. code-block:: json

    {
        "version_id": "<scm_id>",
        "build_time": "YYYY-MM-DD HH:MM:SS.NNNNZ"
    }

* Deployment

.. code-block:: json

    {
        "deployed_at": "YYYY-MM-DD HH:MM:SS.NNNNZ",
        "version": {"rel": "version", "href": "<version_uri>"}
    }

* Certificate

.. code-block:: json

    {
        "name": "<string>",
        "fingerprint": "<string>",
        "commonName": "<string>",
        "subjectAltNames": [
          "<string>",
          ...
        ],
        ...
    }
