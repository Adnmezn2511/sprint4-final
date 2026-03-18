import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom'; // Simule le contexte Router
import Toolbar from '../components/Toolbar';
import { waitFor } from '@testing-library/react';

describe('Toolbar Component', () => {
    test('Le composant se rend correctement', () => {
        render(
            <MemoryRouter> 
                <Toolbar />
            </MemoryRouter>
        );
        expect(document.querySelector('.navbar')).toBeInTheDocument(); // ⬅ Remplace 'navigation' par 'navbar'
    });

    test('Les liens de navigation sont présents', () => {
        render(
            <MemoryRouter>
                <Toolbar />
            </MemoryRouter>
        );
        const links = screen.getAllByRole('link');
        expect(links.length).toBeGreaterThan(0);
    });

    // test('Le menu des paramètres s’affiche au clic', async () => {
    //     render(
    //         <MemoryRouter>
    //             <Toolbar />
    //         </MemoryRouter>
    //     );
    
    //     // Vérifier que le bouton des paramètres existe
    //     const button = document.querySelector('.navbar-parameters');
    //     expect(button).not.toBeNull();
    
    //     if (button) {
    //         fireEvent.click(button); // Simule le clic
    //     }
    
    //     // Vérifier si le menu apparaît après le clic
    //     const menu = document.querySelector('.navbar-parameters-menu');
    //     expect(menu).not.toBeNull();
    
    //     await waitFor(() => {
    //         expect(menu).toHaveClass('open'); // Vérifier que le menu est bien ouvert
    //     });
    // });

    // test('Le menu des paramètres se ferme au clic', async () => {
    //     render(
    //         <MemoryRouter>
    //             <Toolbar />
    //         </MemoryRouter>
    //     );
    
    //     // Vérifier que le bouton des paramètres existe
    //     const button = document.querySelector('.navbar-parameters');
    //     expect(button).not.toBeNull();
    
    //     if (button) {
    //         fireEvent.click(button); // Ouvre le menu
    //     }
    
    //     // Vérifier que le menu des paramètres est bien visible
    //     const menu = document.querySelector('.navbar-parameters-menu');
    //     expect(menu).not.toBeNull();
    //     await waitFor(() => expect(menu).toHaveClass('open')); // Vérifie que le menu est bien ouvert après le premier clic
    
    //     if(button){
    //         fireEvent.click(button); 
    //     }

    //     // fireEvent.click(document.body); // Clic en dehors du menu

    //     // Vérifier que le menu a la classe "close" après le second clic
    //     await waitFor(() => expect(menu).toHaveClass('close'));
    // });
    
    
});
