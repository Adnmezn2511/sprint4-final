// frontend/src/__tests__/MultiplexMA.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import MultiplexMA from '../components/MultiplexMA';

global.fetch = jest.fn();

beforeEach(() => {
    fetch.mockClear();
    fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ nodes: ['GeneA', 'GeneB', 'GeneC'] }),
    });
});

// On passe un state avec couche + tsvs pour simuler la navigation réelle
// MultiplexMA lit useLocation().state.couche et useLocation().state.tsvs
const renderComponent = (layerParam = 'layer1') =>
    render(
        <MemoryRouter initialEntries={[{
            pathname: `/multiplex/${layerParam}`,
            state: {
                couche: layerParam,
                tsvs: ['GeneA\tGeneB\nGeneC\tGeneD\n']
            }
        }]}>
            <Routes>
                <Route path="/multiplex/:nomcouche" element={<MultiplexMA />} />
            </Routes>
        </MemoryRouter>
    );

// ── Rendu ────────────────────────────────────────────────────────────────────
describe('MultiplexMA Component — rendu', () => {

    test('se rend sans crash', () => {
        expect(() => renderComponent()).not.toThrow();
    });

    test('affiche le titre "Random walk Algorithm"', async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByText(/random walk algorithm/i)).toBeInTheDocument();
        });
    });

    test('affiche le champ title', async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
        });
    });

    test('affiche le champ user', async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByLabelText(/user/i)).toBeInTheDocument();
        });
    });

    test('affiche le champ steps', async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByLabelText(/steps/i)).toBeInTheDocument();
        });
    });

    test('affiche le champ top', async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByLabelText(/top/i)).toBeInTheDocument();
        });
    });

    test('affiche le champ restart', async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByLabelText(/restart/i)).toBeInTheDocument();
        });
    });

    test('affiche le bouton Start', async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /start/i })).toBeInTheDocument();
        });
    });
});

// ── Interactions ─────────────────────────────────────────────────────────────
describe('MultiplexMA Component — interactions', () => {

    test('remplir le champ title met à jour la valeur', async () => {
        renderComponent();
        await waitFor(() => screen.getByLabelText(/title/i));
        const input = screen.getByLabelText(/title/i);
        fireEvent.change(input, { target: { value: 'Mon titre' } });
        expect(input.value).toBe('Mon titre');
    });

    test('remplir le champ user met à jour la valeur', async () => {
        renderComponent();
        await waitFor(() => screen.getByLabelText(/user/i));
        const input = screen.getByLabelText(/user/i);
        fireEvent.change(input, { target: { value: 'alice' } });
        expect(input.value).toBe('alice');
    });

    test('clic sur Start sans seeds affiche une alerte', async () => {
        renderComponent();
        await waitFor(() => screen.getByRole('button', { name: /start/i }));
        fireEvent.click(screen.getByRole('button', { name: /start/i }));
        await waitFor(() => {
            expect(screen.getByText(/parameter/i)).toBeInTheDocument();
        });
    });

    test('les noeuds sont chargés depuis les tsvs passés en state', async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByText(/seeds available/i)).toBeInTheDocument();
        });
    });
});