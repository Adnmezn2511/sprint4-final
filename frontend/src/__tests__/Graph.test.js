// frontend/src/__tests__/Graph.test.js
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PlotlyJsonComponent from '../components/Graph';

// Mock react-plotly.js pour éviter les erreurs WebGL en jsdom
jest.mock('react-plotly.js', () => {
    return function MockPlot({ data, layout }) {
        return <div data-testid="plotly-graph">MockPlot</div>;
    };
});

// Mock plotly.js/lib/core
jest.mock('plotly.js/lib/core', () => ({}));

// Mock apiService
jest.mock('../apiService', () => ({
    GraphJson: jest.fn(),
}));
import { GraphJson } from '../apiService';

const DEFAULT_PROPS = {
    seeds: ['GeneA', 'GeneB'],
    nb_iterations: 1,
    top: 10,
    restart: 0.7,
    user: 'alice',
    title: 'Test Graph',
};

beforeEach(() => {
    jest.clearAllMocks();
    process.env.REACT_APP_API_URL = 'http://localhost:8000/';
});

describe('Graph (PlotlyJsonComponent) — rendu', () => {

    test('affiche "Loading ..." pendant le chargement', () => {
        GraphJson.mockReturnValue(new Promise(() => {})); // pending forever
        render(<PlotlyJsonComponent {...DEFAULT_PROPS} />);
        expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    test('affiche le graphe Plotly après chargement réussi', async () => {
        GraphJson.mockResolvedValue({
            data: [{ type: 'scatter', x: [1, 2], y: [1, 2] }],
            layout: { title: 'Test' },
        });
        render(<PlotlyJsonComponent {...DEFAULT_PROPS} />);
        await waitFor(() => {
            expect(screen.getByTestId('plotly-graph')).toBeInTheDocument();
        });
    });

    test('affiche "No data" si GraphJson retourne null', async () => {
        GraphJson.mockResolvedValue(null);
        render(<PlotlyJsonComponent {...DEFAULT_PROPS} />);
        await waitFor(() => {
            expect(screen.getByText(/no data/i)).toBeInTheDocument();
        });
    });

    test('affiche un message d\'erreur si GraphJson échoue', async () => {
        GraphJson.mockRejectedValue(new Error('API down'));
        render(<PlotlyJsonComponent {...DEFAULT_PROPS} />);
        await waitFor(() => {
            expect(screen.getByText(/error/i)).toBeInTheDocument();
        });
    });

    test('appelle GraphJson avec les bons paramètres', async () => {
        GraphJson.mockResolvedValue({ data: [], layout: {} });
        render(<PlotlyJsonComponent {...DEFAULT_PROPS} />);
        await waitFor(() => {
            expect(GraphJson).toHaveBeenCalledWith(
                DEFAULT_PROPS.seeds,
                DEFAULT_PROPS.nb_iterations,
                DEFAULT_PROPS.top,
                DEFAULT_PROPS.restart,
                DEFAULT_PROPS.user,
                DEFAULT_PROPS.title
            );
        });
    });
});