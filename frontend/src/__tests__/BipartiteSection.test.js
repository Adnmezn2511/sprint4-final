// frontend/src/__tests__/BipartiteSection.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import BipartiteSection from '../components/ZipForm/BipartiteSection';

const MOCK_LAYERS = [
    { id: 1, name: 'Genes', files: [] },
    { id: 2, name: 'Diseases', files: [] },
];

const renderComponent = (bipartites = [], setBipartites = jest.fn(), layers = MOCK_LAYERS) =>
    render(
        <BipartiteSection
            bipartites={bipartites}
            setBipartites={setBipartites}
            layers={layers}
        />
    );

describe('BipartiteSection — rendu', () => {

    test('se rend sans crash', () => {
        expect(() => renderComponent()).not.toThrow();
    });

    test('affiche le titre "Bipartite"', () => {
        renderComponent();
        expect(screen.getByText('Bipartite')).toBeInTheDocument();
    });

    test('affiche le bouton "Add Bipartite"', () => {
        renderComponent();
        expect(screen.getByRole('button', { name: /add bipartite/i })).toBeInTheDocument();
    });

    test('affiche les bipartites passés en props', () => {
        const bipartites = [{ id: 1, layer1: 'Genes', layer2: 'Diseases', file: null }];
        renderComponent(bipartites);
        expect(screen.getAllByDisplayValue('Genes').length).toBeGreaterThan(0);
        expect(screen.getAllByDisplayValue('Diseases').length).toBeGreaterThan(0);
    });

    test('affiche les options de layers dans les selects', () => {
        const bipartites = [{ id: 1, layer1: '', layer2: '', file: null }];
        renderComponent(bipartites);
        const options = screen.getAllByText('Genes');
        expect(options.length).toBeGreaterThan(0);
    });
});

describe('BipartiteSection — interactions', () => {

    test('clic sur Add Bipartite appelle setBipartites avec un nouveau bipartite', () => {
        const setBipartites = jest.fn();
        renderComponent([], setBipartites);
        fireEvent.click(screen.getByRole('button', { name: /add bipartite/i }));
        expect(setBipartites).toHaveBeenCalled();
        const result = setBipartites.mock.calls[0][0];
        expect(result).toHaveLength(1);
        expect(result[0]).toMatchObject({ layer1: '', layer2: '', file: null });
    });

    test('changer layer1 appelle setBipartites', () => {
        const setBipartites = jest.fn();
        const bipartites = [{ id: 1, layer1: '', layer2: '', file: null }];
        renderComponent(bipartites, setBipartites);
        const selects = screen.getAllByRole('combobox');
        fireEvent.change(selects[0], { target: { value: 'Genes' } });
        expect(setBipartites).toHaveBeenCalled();
    });

    test('clic sur Delete Bipartite supprime le bipartite', () => {
        const setBipartites = jest.fn();
        const bipartites = [
            { id: 1, layer1: 'Genes', layer2: 'Diseases', file: null },
            { id: 2, layer1: 'Genes', layer2: 'Diseases', file: null },
        ];
        renderComponent(bipartites, setBipartites);
        const deleteButtons = screen.getAllByRole('button', { name: /delete bipartite/i });
        fireEvent.click(deleteButtons[0]);
        const result = setBipartites.mock.calls[0][0];
        expect(result).toHaveLength(1);
        expect(result[0].id).toBe(2);
    });
});