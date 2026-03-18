import '../css/Logs.css';
import { React, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Logs() {
    useEffect(() => {
          document.title = "GM | Logs";
        }, []);

    const handleDownload = () => {
        const fileUrl = '/path/to/your/file.pdf';
        const link = document.createElement('a');
        link.href = fileUrl;
        link.download = 'mon-fichier.pdf'; 
        link.click();
      };

    return (
        <div>
          <div className="logs-container">
            <h2>Logs</h2>
            <table className="log">
              <div className="d-img">
                <i className="fas fa-eye"></i>
              </div>

                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Parameters</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>User</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>
                        ML1
                    </td>
                    <td>
                        S1-P1-100
                    </td>
                    <td>
                        15/02/25
                    </td>
                    <td>
                        17:52:00
                    </td>
                    <td>
                        qchaumette
                    </td>
                    <td>
                      <div className="dl-img" onClick={handleDownload}><i className="fas fa-download"></i></div>
                    </td>
                  </tr>
                </tbody>
            </table>  
          </div>
        </div>
      );
}

export default Logs;
