// frontend/src/__tests__/App.test.js
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';

// Mock Plotly pour éviter les erreurs WebGL
jest.mock('react-plotly.js', () => () => <div data-testid="plotly-mock" />);
jest.mock('plotly.js/lib/core', () => ({}));
jest.mock('../apiService', () => ({
    GraphJson: jest.fn().mockResolvedValue({ data: [], layout: {} }),
    getHistory: jest.fn().mockResolvedValue([]),
    uploadFile: jest.fn(),
}));
jest.mock('jszip', () => jest.fn().mockImplementation(() => ({
    loadAsync: jest.fn().mockResolvedValue({ files: {} }),
})));

// Import des composants individuellement pour tester le routing
import Home from '../components/Home';
import History from '../components/History';
import MultiplexLOAD from '../components/MultiplexLOAD';

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
}));

beforeEach(() => {
    jest.clearAllMocks();
    process.env.REACT_APP_API_URL = 'http://localhost:8000/';
    window.URL.createObjectURL = jest.fn(() => 'blob:fake');
    window.URL.revokeObjectURL = jest.fn();
    global.fetch = jest.fn().mockResolvedValue({
        ok: true, json: async () => [],
    });
});

describe('Routing — pages principales', () => {

    test('route / affiche le composant Home', () => {
        render(<MemoryRouter initialEntries={['/']}><Home /></MemoryRouter>);
        expect(screen.getByText(/PFE/)).toBeInTheDocument();
    });

    test('route /multiplex/ affiche MultiplexLOAD', () => {
        render(<MemoryRouter initialEntries={['/multiplex/']}><MultiplexLOAD /></MemoryRouter>);
        expect(screen.getByText(/load your multiplex/i)).toBeInTheDocument();
    });

    test('route /logs affiche History', () => {
        render(<MemoryRouter initialEntries={['/logs']}><History /></MemoryRouter>);
        expect(screen.getByText(/graph history/i)).toBeInTheDocument();
    });
});