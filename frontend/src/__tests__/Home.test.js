// frontend/src/__tests__/Home.test.js
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import Home from '../components/Home';

describe('Home Component', () => {

    let container;

    beforeEach(() => {
        const result = render(<MemoryRouter><Home /></MemoryRouter>);
        container = result.container;
    });

    test('se rend sans erreur', () => {
        expect(container).toBeTruthy();
    });

    test('le titre du document est défini', () => {
        expect(document.title).toBe('GM | Home');
    });

    test('affiche le mot PFE', () => {
        // PFE est dans un <strong> imbriqué → on cherche dans le texte complet du DOM
        expect(container.textContent).toMatch(/PFE/);
    });

    test('affiche le mot "multiplex"', () => {
        // "multiplex" est au milieu d'une longue phrase → textContent de toute la page
        expect(container.textContent.toLowerCase()).toMatch(/multiplex/);
    });

    test('affiche une description du random walk', () => {
        // Idem, "random walk" est dans un paragraphe long
        expect(container.textContent.toLowerCase()).toMatch(/random walk/);
    });
});