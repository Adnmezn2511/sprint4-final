// frontend/src/__tests__/History.test.js
import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';

// IMPORTANT : jest.mock AVANT les imports des fonctions mockées
jest.mock('../apiService', () => ({
    getHistory: jest.fn(),
    deleteGraph: jest.fn(),
    downloadZip: jest.fn(),
    getGraphById: jest.fn(),
}));

import History from '../components/History';
import { getHistory, deleteGraph, downloadZip, getGraphById } from '../apiService';

// ── Données de test ──────────────────────────────────────────────────────────
const MOCK_HISTORY = [
    {
        id: 1,
        user: 'alice',
        title: 'Graph Alpha',
        created_at: '2025-03-01T10:00:00Z',
        graph_json: { data: [], layout: {} },
    },
    {
        id: 2,
        user: 'bob',
        title: 'Graph Beta',
        created_at: '2025-03-02T12:00:00Z',
        graph_json: { data: [], layout: {} },
    },
];

// ── Setup ────────────────────────────────────────────────────────────────────
beforeEach(() => {
    jest.clearAllMocks();
    window.confirm = jest.fn(() => true);
    window.open = jest.fn();
    window.URL.createObjectURL = jest.fn(() => 'blob:fake-url');
    window.URL.revokeObjectURL = jest.fn();
    window.Plotly = {
        react: jest.fn(),
        purge: jest.fn(),
    };
});

// ── Helper ───────────────────────────────────────────────────────────────────
const renderComponent = () =>
    render(<MemoryRouter><History /></MemoryRouter>);

// ── Tests : rendu initial ────────────────────────────────────────────────────
describe('History Component — rendu initial', () => {

    test('affiche un indicateur de chargement au démarrage', () => {
        getHistory.mockReturnValue(new Promise(() => {}));
        renderComponent();
        expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    test('affiche les entrées après chargement', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        renderComponent();
        await waitFor(() => {
            expect(screen.getByText('Graph Alpha')).toBeInTheDocument();
            expect(screen.getByText('Graph Beta')).toBeInTheDocument();
        });
    });

    test('affiche "No history available" si liste vide', async () => {
        getHistory.mockResolvedValue([]);
        renderComponent();
        await waitFor(() => {
            expect(screen.getByText(/no history available/i)).toBeInTheDocument();
        });
    });

    test('affiche un message d\'erreur si getHistory échoue', async () => {
        getHistory.mockRejectedValue(new Error('Network error'));
        renderComponent();
        await waitFor(() => {
            expect(screen.getByText(/error/i)).toBeInTheDocument();
        });
    });

    test('affiche les colonnes ID, User, Title, Date, Actions', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        expect(screen.getByText(/ID/i)).toBeInTheDocument();
        expect(screen.getByText(/User/i)).toBeInTheDocument();
        expect(screen.getByText(/Title/i)).toBeInTheDocument();
        expect(screen.getByText(/Date/i)).toBeInTheDocument();
    });
});

// ── Tests : actions ──────────────────────────────────────────────────────────
describe('History Component — actions', () => {

    test('clic sur delete appelle deleteGraph avec l\'id correct', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        deleteGraph.mockResolvedValue({});
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        const deleteBtns = document.querySelectorAll('.delete-btn');
        fireEvent.click(deleteBtns[0]);
        await waitFor(() => {
            expect(deleteGraph).toHaveBeenCalledWith(1);
        });
    });

    test('clic sur view appelle getGraphById et ouvre la modal', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        getGraphById.mockResolvedValue({
            id: 1, user: 'alice', title: 'Graph Alpha',
            created_at: '2025-03-01T10:00:00Z',
            graph_json: { data: [], layout: {} },
            parameters: {},
        });
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        fireEvent.click(document.querySelectorAll('.view-btn')[0]);
        await waitFor(() => {
            expect(getGraphById).toHaveBeenCalledWith(1);
        });
    });

    test('clic sur download appelle downloadZip avec l\'id correct', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        downloadZip.mockResolvedValue(undefined);
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        const downloadBtns = document.querySelectorAll('.download-btn');
        fireEvent.click(downloadBtns[0]);
        await waitFor(() => {
            expect(downloadZip).toHaveBeenCalledWith(1);
        });
    });

    test('supprimer une entrée la retire de la liste', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        deleteGraph.mockResolvedValue({});
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        const deleteBtns = document.querySelectorAll('.delete-btn');
        await act(async () => {
            fireEvent.click(deleteBtns[0]);
        });
        await waitFor(() => {
            expect(screen.queryByText('Graph Alpha')).not.toBeInTheDocument();
        });
    });
});

// ── Tests : modal affichage graphe (B2) ──────────────────────────────────────
describe('History Component — modal affichage graphe (B2)', () => {

    const MOCK_GRAPH_DETAIL = {
        id: 1,
        user: 'alice',
        title: 'Graph Alpha',
        created_at: '2025-03-01T10:00:00Z',
        graph_json: { data: [], layout: {} },
        parameters: { Seeds: ['GeneA', 'GeneB'], Iterations: 3 },
    };

    test('clic sur view appelle getGraphById avec le bon id', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        getGraphById.mockResolvedValue(MOCK_GRAPH_DETAIL);
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        fireEvent.click(document.querySelectorAll('.view-btn')[0]);
        await waitFor(() => {
            expect(getGraphById).toHaveBeenCalledWith(1);
        });
    });

    test('la modal s\'affiche après clic sur view', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        getGraphById.mockResolvedValue(MOCK_GRAPH_DETAIL);
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        fireEvent.click(document.querySelectorAll('.view-btn')[0]);
        await waitFor(() => {
            expect(screen.getByTestId('graph-modal')).toBeInTheDocument();
        });
    });

    test('le titre du graphe s\'affiche dans la modal', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        getGraphById.mockResolvedValue(MOCK_GRAPH_DETAIL);
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        fireEvent.click(document.querySelectorAll('.view-btn')[0]);
        await waitFor(() => {
            expect(screen.getByTestId('graph-modal')).toBeInTheDocument();
            expect(screen.getAllByText('Graph Alpha').length).toBeGreaterThan(0);
        });
    });

    test('fermeture de la modal au clic sur le bouton ✕', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        getGraphById.mockResolvedValue(MOCK_GRAPH_DETAIL);
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        fireEvent.click(document.querySelectorAll('.view-btn')[0]);
        await waitFor(() => screen.getByTestId('graph-modal'));
        fireEvent.click(screen.getByLabelText('Fermer'));
        await waitFor(() => {
            expect(screen.queryByTestId('graph-modal')).not.toBeInTheDocument();
        });
    });

    test('les paramètres multi-seeds s\'affichent dans la modal', async () => {
        getHistory.mockResolvedValue(MOCK_HISTORY);
        getGraphById.mockResolvedValue(MOCK_GRAPH_DETAIL);
        renderComponent();
        await waitFor(() => screen.getByText('Graph Alpha'));
        fireEvent.click(document.querySelectorAll('.view-btn')[0]);
        await waitFor(() => {
            expect(screen.getByText(/GeneA/)).toBeInTheDocument();
            expect(screen.getByText(/GeneB/)).toBeInTheDocument();
        });
    });
});