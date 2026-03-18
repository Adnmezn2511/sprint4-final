import { React, useEffect } from 'react';
import '../css/Credits.css'; 

function Credits() {
    useEffect(() => {
      document.title = "GM | Credits";
    }, []);

  const devs = [
    {
      name: 'Quentin Chaumette',
      avatar: 'https://via.placeholder.com/50', 
      email: 'quentin.chaumette-aime@etu.u-bordeaux.fr',
      avatar: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnMfMseIdDUsScDNj5ewigeK6A3d3y2-EDw&s',
    },
    {
      name: 'Quentin Bret',
      avatar: 'https://via.placeholder.com/50', 
      email: 'quentin.bret@etu.u-bordeaux.fr',
      avatar: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnMfMseIdDUsScDNj5ewigeK6A3d3y2-EDw&s',
    },
    {
      name: 'Odrian Tarrieu',
      avatar: 'https://via.placeholder.com/50', 
      email: 'odrian.tarrieu@etu.u-bordeaux.fr',
      avatar: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnMfMseIdDUsScDNj5ewigeK6A3d3y2-EDw&s',
    },
    {
      name: 'Corentin Drezen',
      avatar: 'https://via.placeholder.com/50', 
      email: 'corentin.drezen@etu.u-bordeaux.fr',
      avatar: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnMfMseIdDUsScDNj5ewigeK6A3d3y2-EDw&s',
    },
    {
      name: 'Christophe Say-Liang-Fat',
      avatar: 'https://via.placeholder.com/50', 
      email: 'christophe.say-liang-fat@etu.u-bordeaux.fr',
      avatar: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnMfMseIdDUsScDNj5ewigeK6A3d3y2-EDw&s',
    },
    {
      name: 'Thomas Castaigna',
      avatar: 'https://via.placeholder.com/50', 
      email: 'thomas.castaigna@etu.u-bordeaux.fr',
      avatar: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnMfMseIdDUsScDNj5ewigeK6A3d3y2-EDw&s',
    },
  ];

  const searchers = [
    {
      name: 'Patricia Thebault',
      avatar: 'https://via.placeholder.com/50', 
      email: 'patricia.thebault@u-bordeaux.fr',
      avatar: 'https://www.postlab.fr/media/cache/squared_thumbnail_medium/uploads/lab_logo/logo-labri-649efaeb7feaf.png',
    },
    {
      name: 'Elodie Darbo',
      avatar: 'https://via.placeholder.com/50', 
      email: 'elodie.darbo@u-bordeaux.fr',
      avatar: 'https://www.postlab.fr/media/cache/squared_thumbnail_medium/uploads/lab_logo/logo-labri-649efaeb7feaf.png',
    },
    {
      name: 'Francoise Metuekam',
      avatar: 'https://via.placeholder.com/50', 
      email: 'francoise.metuekam@u-bordeaux.fr',
      avatar: 'https://www.postlab.fr/media/cache/squared_thumbnail_medium/uploads/lab_logo/logo-labri-649efaeb7feaf.png',
    },
  ];

  return (
    <header>
      <div className="project-infos">
        <img 
          src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnMfMseIdDUsScDNj5ewigeK6A3d3y2-EDw&s" 
          alt="logo" 
          width="40" 
          height="40" 
        />
        <p>
          Projet de fin d'Etudes (<strong>PFE</strong>) carried out by six students from Master 2 Génie Logiciel.
        </p>
      </div>
        
      <div className="dev-team">
        <p><strong>Dev team</strong></p>
        <div className="contacts">
          {devs.map((contact, index) => (
            <div key={index} className="contact-card">
              <img src={contact.avatar} alt={contact.name} className="contact-avatar-ub" />
              <div className="contact-info">
                <h3>{contact.name}</h3>
                <p>{contact.email}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="searchers-team">
        <p><strong>Researchers behind this project</strong></p>
        <div className="contacts">
          {searchers.map((contact, index) => (
            <div key={index} className="contact-card">
              <img src={contact.avatar} alt={contact.name} className="contact-avatar-labri" />
              <div className="contact-info">
                <h3>{contact.name}</h3>
                <p>{contact.email}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="ubxlabri">
      <img src={"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnMfMseIdDUsScDNj5ewigeK6A3d3y2-EDw&s"} alt={"ubx"} className="ubxlabri-ub" />
      <img src={"https://www.postlab.fr/media/cache/squared_thumbnail_medium/uploads/lab_logo/logo-labri-649efaeb7feaf.png"} alt={"labrix"} className="ubxlabri-labri" />
      <a className="ubxlabri-aub" href="https://www.u-bordeaux.fr/">Université de Bordeaux</a>
      <a className="ubxlabri-alabri" href="https://www.labri.fr/">LaBRI</a>        
      </div>
        <div className="creds-blank-container"> <p> </p></div>
    </header>
  );
}

export default Credits;
