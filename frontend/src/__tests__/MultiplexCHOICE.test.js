// frontend/src/__tests__/MultiplexCHOICE.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import MultiplexCHOICE from '../components/MultiplexCHOICE';

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
    useLocation: () => ({
        state: {
            tsvDict: {
                Genes: ['GeneA\tGeneB\n', 'GeneC\tGeneD\n'],
                Diseases: ['Disease1\tDisease2\n'],
            },
        },
    }),
}));

beforeEach(() => {
    jest.clearAllMocks();
});

const renderComponent = () =>
    render(<MemoryRouter><MultiplexCHOICE /></MemoryRouter>);

describe('MultiplexCHOICE — rendu', () => {

    test('se rend sans crash', () => {
        expect(() => renderComponent()).not.toThrow();
    });

    test('affiche le titre "Layer selection"', () => {
        renderComponent();
        expect(screen.getByText(/layer selection/i)).toBeInTheDocument();
    });

    test('affiche le select des couches', () => {
        renderComponent();
        expect(document.querySelector('#coucheSelect')).toBeInTheDocument();
    });

    test('affiche les options de couches depuis tsvDict', () => {
        renderComponent();
        expect(screen.getByText('Genes')).toBeInTheDocument();
        expect(screen.getByText('Diseases')).toBeInTheDocument();
    });

    test('affiche l\'option vide par défaut', () => {
        renderComponent();
        expect(screen.getByText('Layer')).toBeInTheDocument();
    });

    test('définit le titre du document', () => {
        renderComponent();
        expect(document.title).toBe("GM | Multiplex's layer choice");
    });
});

describe('MultiplexCHOICE — interactions', () => {

    test('soumettre sans sélection affiche un message d\'erreur', async () => {
        renderComponent();
        const submitBtn = document.querySelector('.m-change-couche');
        fireEvent.click(submitBtn);
        await waitFor(() => {
            expect(screen.getByText(/please choose a layer/i)).toBeInTheDocument();
        });
    });

    test('changer la sélection met à jour la valeur', () => {
        renderComponent();
        const select = document.querySelector('#coucheSelect');
        fireEvent.change(select, { target: { value: 'Genes' } });
        expect(select.value).toBe('Genes');
    });

    test('soumettre avec une couche sélectionnée appelle navigate', async () => {
        renderComponent();
        const select = document.querySelector('#coucheSelect');
        fireEvent.change(select, { target: { value: 'Genes' } });

        const submitBtn = document.querySelector('.m-change-couche');
        fireEvent.click(submitBtn);

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith(
                '/multiplex/Genes',
                expect.objectContaining({
                    state: expect.objectContaining({ couche: 'Genes' }),
                })
            );
        });
    });

    test('navigate est appelé avec les tsvs corrects', async () => {
        renderComponent();
        const select = document.querySelector('#coucheSelect');
        fireEvent.change(select, { target: { value: 'Diseases' } });

        const submitBtn = document.querySelector('.m-change-couche');
        fireEvent.click(submitBtn);

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith(
                '/multiplex/Diseases',
                expect.objectContaining({
                    state: expect.objectContaining({
                        tsvs: ['Disease1\tDisease2\n'],
                    }),
                })
            );
        });
    });
});