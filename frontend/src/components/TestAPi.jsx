import React from 'react';

import { testapi } from '../apiService';

function App() {
    React.useEffect(() => {
        const result = testapi();
        console.log(result);
    }, []);

    return (
        <div>
            Check the console for the API call result.
        </div>
    );
}

export default App;