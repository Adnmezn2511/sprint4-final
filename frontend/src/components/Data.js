import '../css/Data.css';
import { React, useEffect } from 'react';

function Data() {
  useEffect(() => {
    document.title = "GM | Uses";
  }, []);

  return (
    <div>
      <h2 className="uses-title">Here's how to setup your input</h2>
      <div className="arc-type">
        <h3>How to structure your .zip</h3>
      </div>
      <div className="tsv-type">
        <h3>How to structure your .tsv</h3>
      </div>
    </div>
  );
}

export default Data;
