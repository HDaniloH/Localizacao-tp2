import { useState, useEffect } from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Sun, Moon, Menu } from 'lucide-react';

export function Layout() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar Responsiva */}
      <nav className="bg-white dark:bg-gray-800 shadow-md p-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-blue-600 dark:text-blue-400">
            UrbanReport
          </Link>
          
          <div className="flex items-center gap-4">
            {/* Links Desktop */}
            <div className="hidden md:flex gap-4">
              <Link to="/login" className="hover:text-blue-500">Login</Link>
              <Link to="/admin/categorias" className="hover:text-blue-500">Categorias (US05)</Link>
            </div>

            <button 
              onClick={() => setIsDarkMode(!isDarkMode)} 
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            {/* Menu Mobile */}
            <button className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
              <Menu size={24} />
            </button>
          </div>
        </div>
        
        {/* Dropdown Mobile */}
        {menuOpen && (
          <div className="md:hidden flex flex-col gap-2 mt-4 pb-2 border-t dark:border-gray-700 pt-2">
            <Link to="/login" className="block py-2">Login</Link>
            <Link to="/admin/categorias" className="block py-2">Categorias (US05)</Link>
          </div>
        )}
      </nav>

      {/* Container Principal */}
      <main className="flex-1 w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
        <Outlet />
      </main>
    </div>
  );
}