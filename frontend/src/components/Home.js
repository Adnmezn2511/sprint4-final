import '../css/Home.css';
import { React, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Home() {
    useEffect(() => {
      document.title = "GM | Home";
    }, []);

  return (
    <div className="home-global-container">
      <div className="welcome-container">
      <p>Welcome to our website ! This is a Master 2 Génie Logiciel Projet de Fin d'Etudes (<strong>PFE</strong>) from the University of Bordeaux.</p>
    </div>
    <h3>Visualization of multiplex graphs and random walks</h3>
    <div className="subject-exp-container">

      <p>Biological networks offer a way of modeling and analyzing interactions between different biological entities.
        Each type of information can be represented as a graph, and a multiplex graph integrates several layers of information
        where the nodes represent the intersections between these layers. The main interest of a multiplex biological graph
        lies in its ability to model complementary information. For example, one layer may illustrate the relationships between
        genes, proteins and diseases, while another may represent co-expressed genes linked to a phenotype or pathology.

        A random walk algorithm exploits this multiplexed information to make predictions, such as identifying the genes involved in a given disease.
      </p>
    </div>

    <div className="subject-container">
      <p>The aim of this project is to develop a web application that will first enable users to load and
        visualize several graphs. Next, the user will be able to select a node type or a specific element
        in order to identify a set of candidates by applying the random walk algorithm. The graph displayed
        will then be dynamically updated to illustrate the path taken by the algorithm.
      </p>
    </div>
    <div className="blank-container"> <p> </p></div>
  </div>
  );
}

export default Home;


