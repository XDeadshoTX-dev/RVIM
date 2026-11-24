import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { todoAPI, authAPI } from '../api/api';
import { useLocalStorage } from '../hooks/useLocalStorage';

export default function Workspace() {
  const navigate = useNavigate();
  
  // Стани для аватарки та імені (ЛР2)
  const [avatarUrl, setAvatarUrl] = useState('https://ui-avatars.com/api/?name=User&background=667eea&color=fff&size=128');
  const [userName, setUserName] = useState('Користувач');
  
  const [lists, setLists] = useState([]);
  const [selectedList, setSelectedList] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newListTitle, setNewListTitle] = useState('');
  const [newItemTitle, setNewItemTitle] = useState('');
  const [editingListId, setEditingListId] = useState(null);
  const [editingItem, setEditingItem] = useState(null);
  const [editingDescription, setEditingDescription] = useState(false);
  const [descriptionDraft, setDescriptionDraft] = useState('');
  
  const [theme, setTheme] = useLocalStorage('todo_theme', 'light');
  const [lastListId, setLastListId] = useLocalStorage('todo_last_list', null);
  
  const descriptionRef = useRef(null);

  // Завантаження даних користувача та аватарки з GitHub (ЛР2)
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const meRes = await authAPI.getMe();
        const firstName = meRes.data.firstName || '';
        const lastName = meRes.data.lastName || '';
        setUserName(`${firstName} ${lastName}`.trim() || 'Користувач');
        
        if (meRes.data.email) {
          try {
            const githubRes = await authAPI.getGithubAvatar(meRes.data.email);
            if (githubRes.data.avatarUrl) {
              setAvatarUrl(githubRes.data.avatarUrl);
            }
          } catch (err) {
            console.log('GitHub API не знайшов аватар, використовується fallback');
          }
        }
      } catch (err) {
        console.error('Не вдалося отримати дані користувача', err);
      }
    };
    fetchUserData();
  }, []);

  useEffect(() => {
    loadLists();
  }, []);

  useEffect(() => {
    if (editingDescription && descriptionRef.current) {
      descriptionRef.current.focus();
      const length = descriptionRef.current.value.length;
      descriptionRef.current.setSelectionRange(length, length);
    }
  }, [editingDescription]);

  useEffect(() => {
    if (lastListId && lists.length > 0 && !selectedList) {
      const last = lists.find(l => l.id === lastListId);
      if (last) handleSelectList(last);
    }
  }, [lists, lastListId]);

  const loadLists = async () => {
    try {
      setLoading(true);
      const response = await todoAPI.getLists();
      setLists(response.data.data || []);
    } catch (error) {
      console.error('Failed to load lists:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadItems = async (listId) => {
    try {
      const response = await todoAPI.getListItems(listId);
      setItems(response.data.data || []);
    } catch (error) {
      console.error('Failed to load items:', error);
    }
  };

  const handleSelectList = (list) => {
    setSelectedList(list);
    setLastListId(list.id);
    setEditingListId(null);
    setEditingItem(null);
    setEditingDescription(false);
    setDescriptionDraft(list.description || '');
    setNewItemTitle('');
    loadItems(list.id);
  };

  const handleCreateList = async (e) => {
    e.preventDefault();
    if (!newListTitle.trim()) return;
    
    try {
      const response = await todoAPI.createList({ title: newListTitle });
      setLists(prev => [response.data.data, ...prev]);
      setNewListTitle('');
    } catch (error) {
      alert(error.response?.data?.error || 'Помилка створення списку');
    }
  };

  const handleDeleteList = async (listId) => {
    if (!confirm('Видалити список та всі його завдання?')) return;
    try {
      await todoAPI.deleteList(listId);
      setLists(prev => prev.filter(l => l.id !== listId));
      if (selectedList?.id === listId) {
        setSelectedList(null);
        setItems([]);
        setEditingDescription(false);
      }
    } catch (error) {
      alert('Помилка видалення');
    }
  };

  const handleEditList = async (listId, newTitle) => {
    if (!newTitle.trim()) {
      setEditingListId(null);
      return;
    }
    try {
      const response = await todoAPI.updateList(listId, { title: newTitle });
      setLists(prev => prev.map(l => l.id === listId ? response.data.data : l));
      setEditingListId(null);
      if (selectedList?.id === listId) setSelectedList(response.data.data);
    } catch (error) {
      alert('Помилка редагування');
    }
  };

  const startEditDescription = () => {
    setDescriptionDraft(selectedList.description || '');
    setEditingDescription(true);
  };

  const saveDescription = async () => {
    if (!selectedList) return;
    const newDescription = descriptionDraft.trim() || null;
    const oldDescription = selectedList.description || null;
    
    if (newDescription === oldDescription) {
      setEditingDescription(false);
      return;
    }
    
    try {
      const response = await todoAPI.updateList(selectedList.id, { description: newDescription });
      const updated = response.data.data;
      setLists(prev => prev.map(l => l.id === updated.id ? updated : l));
      setSelectedList(updated);
      setEditingDescription(false);
    } catch (error) {
      alert('Помилка збереження опису');
    }
  };

  const cancelEditDescription = () => {
    setDescriptionDraft(selectedList?.description || '');
    setEditingDescription(false);
  };

  const handleDescriptionKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      saveDescription();
    } else if (e.key === 'Escape') {
      cancelEditDescription();
    }
  };

  const handleCreateItem = async (e) => {
    e.preventDefault();
    if (!newItemTitle.trim() || !selectedList) return;
    try {
      const response = await todoAPI.createItem({ listId: selectedList.id, title: newItemTitle });
      setItems(prev => [response.data.data, ...prev]);
      setNewItemTitle('');
    } catch (error) {
      alert(error.response?.data?.error || 'Помилка створення завдання');
    }
  };

  const handleDeleteItem = async (itemId) => {
    if (!confirm('Видалити завдання?')) return;
    try {
      await todoAPI.deleteItem(itemId);
      setItems(prev => prev.filter(i => i.id !== itemId));
    } catch (error) {
      alert('Помилка видалення');
    }
  };

  const handleEditItem = async (itemId, newTitle) => {
    if (!newTitle.trim()) {
      setEditingItem(null);
      return;
    }
    try {
      const response = await todoAPI.updateItem(itemId, { title: newTitle });
      setItems(prev => prev.map(i => i.id === itemId ? response.data.data : i));
      setEditingItem(null);
    } catch (error) {
      alert('Помилка редагування');
    }
  };

  const handleLogOut = async () => {
    try {
      await authAPI.logOut();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      navigate('/log-in');
    }
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div>Завантаження...</div>
      </div>
    );
  }

  return (
    <div style={{...styles.container, background: theme === 'dark' ? '#1a1a2e' : '#f5f7fa', color: theme === 'dark' ? '#eee' : '#333'}}>
      <header style={styles.header}>
        <h1 style={styles.logo}>📝 Todo Manager</h1>
        
        <div style={styles.userProfile}>
          <img 
            src={avatarUrl} 
            alt="Avatar" 
            style={styles.avatar} 
            title={userName}
          />
          <span style={styles.userName}>{userName}</span>
          <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} style={styles.themeBtn}>
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <button onClick={handleLogOut} style={styles.logOutButton}>
            Вийти
          </button>
        </div>
      </header>

      <div style={styles.main}>
        <aside style={styles.sidebar}>
          <form onSubmit={handleCreateList} style={styles.newListForm}>
            <input
              type="text"
              placeholder="Назва нового списку"
              value={newListTitle}
              onChange={(e) => setNewListTitle(e.target.value)}
              style={styles.input}
            />
            <button type="submit" style={styles.addBtn}>+ Додати</button>
          </form>

          <div style={styles.listContainer}>
            {lists.length === 0 ? (
              <p style={styles.emptyText}>Немає списків. Створіть перший!</p>
            ) : (
              lists.map(list => (
                <div
                  key={list.id}
                  style={{
                    ...styles.listItem,
                    ...(selectedList?.id === list.id ? styles.listItemActive : {}),
                  }}
                >
                  {editingListId === list.id ? (
                    <input
                      type="text"
                      defaultValue={list.title}
                      autoFocus
                      onBlur={(e) => handleEditList(list.id, e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleEditList(list.id, e.target.value);
                        if (e.key === 'Escape') setEditingListId(null);
                      }}
                      style={styles.editInput}
                    />
                  ) : (
                    <>
                      <span onClick={() => handleSelectList(list)} style={styles.listTitle}>
                        {list.title}
                      </span>
                      <div style={styles.listActions}>
                        <button onClick={() => setEditingListId(list.id)} style={styles.iconBtn} title="Редагувати">✏️</button>
                        <button onClick={() => handleDeleteList(list.id)} style={styles.iconBtn} title="Видалити">🗑️</button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </aside>

        <main style={styles.content}>
          {selectedList ? (
            <>
              <h2 style={styles.contentTitle}>{selectedList.title}</h2>

              <div style={styles.descriptionWrapper}>
                {editingDescription ? (
                  <textarea
                    ref={descriptionRef}
                    value={descriptionDraft}
                    onChange={(e) => setDescriptionDraft(e.target.value)}
                    onKeyDown={handleDescriptionKeyDown}
                    onBlur={saveDescription}
                    placeholder="Додайте опис списку..."
                    style={styles.descriptionTextarea}
                    rows={3}
                  />
                ) : (
                  <div
                    onClick={startEditDescription}
                    style={{
                      ...styles.descriptionText,
                      ...(selectedList.description ? {} : styles.descriptionPlaceholder),
                    }}
                    title="Натисніть щоб редагувати"
                  >
                    {selectedList.description || 'Додайте опис списку...'}
                  </div>
                )}
                {editingDescription && (
                  <div style={styles.descriptionHint}>
                    Enter — зберегти • Shift+Enter — новий рядок • Esc — скасувати
                  </div>
                )}
              </div>
              
              <form onSubmit={handleCreateItem} style={styles.newItemForm}>
                <input
                  type="text"
                  placeholder="Нове завдання"
                  value={newItemTitle}
                  onChange={(e) => setNewItemTitle(e.target.value)}
                  style={styles.input}
                />
                <button type="submit" style={styles.addBtn}>+ Додати</button>
              </form>

              <div style={styles.itemsContainer}>
                {items.length === 0 ? (
                  <p style={styles.emptyText}>Немає завдань у цьому списку</p>
                ) : (
                  items.map(item => (
                    <div key={item.id} style={styles.itemCard}>
                      {editingItem === item.id ? (
                        <input
                          type="text"
                          defaultValue={item.title}
                          autoFocus
                          onBlur={(e) => handleEditItem(item.id, e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleEditItem(item.id, e.target.value);
                            if (e.key === 'Escape') setEditingItem(null);
                          }}
                          style={styles.editInput}
                        />
                      ) : (
                        <>
                          <span style={styles.itemTitle}>{item.title}</span>
                          <div style={styles.itemActions}>
                            <button onClick={() => setEditingItem(item.id)} style={styles.iconBtn}>✏️</button>
                            <button onClick={() => handleDeleteItem(item.id)} style={styles.iconBtn}>🗑️</button>
                          </div>
                        </>
                      )}
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div style={styles.emptyState}>
              <div style={{ fontSize: '64px', marginBottom: '16px' }}>📋</div>
              <h2>Оберіть список</h2>
              <p>Створіть новий список або оберіть існуючий</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', display: 'flex', flexDirection: 'column', transition: 'background 0.3s' },
  loadingContainer: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', color: '#666' },
  header: { background: 'white', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e0e0e0', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' },
  userProfile: { display: 'flex', alignItems: 'center', gap: '12px' },
  avatar: { width: '40px', height: '40px', borderRadius: '50%', objectFit: 'cover', border: '2px solid #667eea', cursor: 'pointer' },
  userName: { fontSize: '14px', fontWeight: '600', color: '#333', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  themeBtn: { padding: '8px', background: '#f0f0f0', border: 'none', borderRadius: '50%', cursor: 'pointer', fontSize: '16px' },
  logo: { margin: 0, fontSize: '24px', color: '#333' },
  logOutButton: { padding: '8px 16px', background: '#e74c3c', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' },
  main: { display: 'flex', flex: 1, overflow: 'hidden' },
  sidebar: { width: '320px', background: 'white', borderRight: '1px solid #e0e0e0', padding: '20px', overflowY: 'auto' },
  newListForm: { display: 'flex', gap: '8px', marginBottom: '20px' },
  input: { flex: 1, padding: '10px 12px', border: '1px solid #ddd', borderRadius: '6px', fontSize: '14px', outline: 'none' },
  addBtn: { padding: '10px 16px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '600', fontSize: '14px' },
  listContainer: { display: 'flex', flexDirection: 'column', gap: '8px' },
  listItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', borderRadius: '6px', cursor: 'pointer', transition: 'background 0.2s' },
  listItemActive: { background: '#e8ecff' },
  listTitle: { flex: 1, fontSize: '14px', color: '#333' },
  listActions: { display: 'flex', gap: '4px' },
  iconBtn: { background: 'transparent', border: 'none', cursor: 'pointer', padding: '4px 8px', fontSize: '14px', borderRadius: '4px' },
  content: { flex: 1, padding: '32px', overflowY: 'auto' },
  contentTitle: { margin: '0 0 8px 0', fontSize: '28px', color: '#333' },
  descriptionWrapper: { marginBottom: '24px' },
  descriptionText: { padding: '8px 12px', fontSize: '15px', color: '#555', cursor: 'text', borderRadius: '6px', border: '1px solid transparent', transition: 'all 0.15s ease', minHeight: '24px', whiteSpace: 'pre-wrap', wordBreak: 'break-word', lineHeight: '1.5' },
  descriptionPlaceholder: { color: '#aaa', fontStyle: 'italic' },
  descriptionTextarea: { width: '100%', padding: '8px 12px', fontSize: '15px', color: '#333', border: '1px solid #667eea', borderRadius: '6px', outline: 'none', resize: 'vertical', fontFamily: 'inherit', lineHeight: '1.5', minHeight: '60px', background: 'white' },
  descriptionHint: { marginTop: '4px', fontSize: '12px', color: '#999', paddingLeft: '4px' },
  newItemForm: { display: 'flex', gap: '8px', marginBottom: '24px' },
  itemsContainer: { display: 'flex', flexDirection: 'column', gap: '8px' },
  itemCard: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' },
  itemTitle: { flex: 1, fontSize: '15px', color: '#333' },
  itemActions: { display: 'flex', gap: '4px' },
  editInput: { flex: 1, padding: '8px 12px', border: '1px solid #667eea', borderRadius: '4px', fontSize: '14px', outline: 'none' },
  emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#999', textAlign: 'center' },
  emptyText: { color: '#999', textAlign: 'center', padding: '20px' },
};