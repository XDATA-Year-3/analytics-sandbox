Running NetworkX analyses in Clique
===================================

Since analyses within Clique are backed by Romanesco, Clique graphs can
be sent to a Romanesco worker as a NetworkX graph.

Running Titan analyses in Clique using Gremlin
==============================================

Infrastructure
--------------

The infrastructure for Titan/Rexster is setup using Docker. There is a
container for:

-  Titan/Rexster
-  Cassandra
-  ElasticSearch

To setup the entire stack, the following assumes Docker is installed,
and the file etc/titan-rexster.props.tpl exists.

.. code:: bash

      docker run -d --name es elasticsearch
      docker run -d --name cs spotify/cassandra

      docker run -d --name titan-rexster \
             --link es:elasticsearch \
             --link cs:cassandra \
             apobbati/titan-rexster

      CASSANDRA_IP=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' cs)

      sed "s/{{CASSANDRA_HOSTNAME}}/${CASSANDRA_IP}/" etc/titan-rexster.props.tpl > titan-rexster.props

      echo "elasticsearch: " $(docker inspect --format '{{ .NetworkSettings.IPAddress }}' es)
      echo "cassandra:     " $(docker inspect --format '{{ .NetworkSettings.IPAddress }}' cs)
      echo "titan-rexster: " $(docker inspect --format '{{ .NetworkSettings.IPAddress }}' titan-rexster)

Once run, the IP addresses of each of the relevant containers should be
printed, and a titan-rexster.props file will have the information
Gremlin needs to run.

Interacting with the Gremlin REPL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the titan https://github.com/thinkaurelius/titan/wiki/Downloads
page, download Titan 0.5.4 with Hadoop 2, unpack it, and run the
following:

.. code:: bash

      ./titan-0.5.4-hadoop2/bin/gremlin.sh

      # When within the gremlin repl, execute
      g = TitanFactory.open('titan-rexster.props')

      # g now references the graph represented in Titan/Cassandra

Running an analysis from Clique
-------------------------------

The Clique Analyst's Notebook viewer application contains some infrastructure
for running analyses the entire Clique graph (regardless of how much of the
graph is visible on screen).  To run the example computation that ships with the
application, follow these steps:

1. Generate the example graph data:

.. code:: bash

    python graph/make-graph.py | mongoimport -d mydb -c mycollection --drop

This is a very small graph that will suffice for demonstration purposes.

2. Build the Clique ANB application:

.. code:: bash

    git clone https://github.com/XDATA-Year-3/clique-anb.git
    cd clique-anb
    git checkout 9d51f1da2b6d96eb9c6ff548311099dc139adc8e
    git reset --hard

    npm install
    gulp
    gulp serve

This will build and serve the Clique ANB application on localhost, port 3000.
Before using the app, we need to do a bit of configuration.

3. Edit the file ``anb.json`` to configure the application:

.. code:: bash

    cd build/site
    vim anb.json

The file should look like this:

.. code:: javascript

    {
        "database": "mydb",
        "collection": "mycollection",

        "titan": "http://<titan-rexster-IP-address-from-above>/graphs/graph"
    }

4. Open the application by visiting http://localhost:3000?label=a&radius=1 in
   your browser.

5. There is a panel entitled "Graph", with a button marked "Node Centrality" in
   it.  If you click that button, you will initiate a Romanesco job that sends
   the graph data to the Titan server you set up earlier, waits for the the
   server to compute nodal centralities on all the nodes, then returns that
   result to the browser.  If you open the developer console, you should see an
   object mapping node keys to centralities.

Anatomy of Clique-Romanesco job
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the button is clicked, an ajax request is made to `this Tangelo service
<https://github.com/XDATA-Year-3/clique-anb/blob/6732fb47fdab22122965638f5dd001659df8671a/src/assets/tangelo/romanesco/degree_centrality/workflow.py>`_.
The ``run()`` function of that service takes as input two URLs - one for the
Rexster REST API of the Clique graph, and one for the Rexster API of the Titan
server.  In the application, these are automatically generated from the
structure of the Tangelo application itself, and the configuration data supplied
in step 3 above.

The service is relatively straightforward - it sets up a Romanesco pipeline
containing a "rexster copy" and a "gremlin script" task; these have their
respective source code `here
<https://github.com/XDATA-Year-3/clique-anb/blob/6732fb47fdab22122965638f5dd001659df8671a/src/assets/tangelo/romanesco/degree_centrality/rexster_copy.py>`_
and `here
<http://github.com/XDATA-Year-3/clique-anb/blob/6732fb47fdab22122965638f5dd001659df8671a/src/assets/tangelo/romanesco/degree_centrality/rexster_gremlin.py>`_.
The service runs this pipeline, extracts the results, and returns them to the
caller.  In this case, the caller is the browser, which then prints the results
out on the console.  Other options would be to display the data on screen, or
thread it back through the Clique graph database to make them persist across
Clique sessions.

Running a smaller job
~~~~~~~~~~~~~~~~~~~~~

The Clique ANB application contains one other example of running a smaller job,
on just the currently visible subgraph, using inline Romanesco code.  To execute
an example job, select a node, then click on the button marked "Centrality" in
the Node panel.  You should see a browser alert reporting the betweenness
centrality of the selected node.

This job is defined wholly within `this Tangelo service
<https://github.com/XDATA-Year-3/clique-anb/blob/6732fb47fdab22122965638f5dd001659df8671a/src/assets/tangelo/romanesco/centrality.py>`_.
To prepare the data for this job, the JavaScript code prepares the subgraph in
an appropriate format for the Romanesco job, `here
<https://github.com/XDATA-Year-3/clique-anb/blob/6732fb47fdab22122965638f5dd001659df8671a/src/js/index.js#L523-L559>`_.
This code queries the visible subgraph model for nodes and links, then sends
that data along with the identity of the selected node, to the Romanesco job,
which computes the node's betweenness centrality, and reports it back to the
browser.  As before, the client then has the option of displaying the answer, or
persisting it to the database, etc.
