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
