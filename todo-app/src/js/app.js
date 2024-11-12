class TodoApp {
	constructor() {
		//this.todos = JSON.parse(localStorage.getItem('todos')) || [];
		this.API_URL = 'http://localhost:3000/api/todos';
		this.todos = []; // 빈 배열로 초기화
		this.initializeElements();
		this.addEventListeners();
		this.initializeSortable();
		//this.renderTodos();
		// localStorage.getItem 대신 API 호출
		this.loadTodos().then(() => {  // loadTodos 완료 후
			this.checkDueDates();
			setInterval(() => this.checkDueDates(), 60000);
		});
	}

	initializeElements() {
		this.form = document.getElementById('todo-form');
		this.input = document.getElementById('todo-input');
		this.titleInput = document.getElementById('todo-title');
		this.contentInput = document.getElementById('todo-content');
		this.dueDate = document.getElementById('due-date');
		this.todoList = document.getElementById('todo-list');
		this.statusFilter = document.getElementById('status-filter');
		this.sortOption = document.getElementById('sort-option');
		this.searchInput = document.getElementById('search');
	}

	addEventListeners() {
		this.form.addEventListener('submit', (e) => this.handleSubmit(e));
		this.statusFilter.addEventListener('change', () => this.renderTodos());
		this.sortOption.addEventListener('change', () => this.renderTodos());
		this.searchInput.addEventListener('input', () => this.renderTodos());
	}

	initializeSortable() {
		new Sortable(this.todoList, {
			animation: 150,
			handle: '.drag-handle',
			onEnd: (evt) => {
				const items = [...this.todoList.children];
				this.todos = items.map(item =>
					//this.todos.find(todo => todo._id === parseInt(item.dataset.id))
					this.todos.find(todo => todo._id === item.dataset.id)
				);
				this.saveTodos();
			}
		});
	}

	showNotification(message, type = 'warning') {
		const notification = document.createElement('div');
		notification.className = `notification ${type}`;
		notification.textContent = message;

		const notificationArea = document.getElementById('notification-area');
		notificationArea.appendChild(notification);

		setTimeout(() => {
			notification.remove();
		}, 5000);
	}

	checkDueDates() {
		const now = new Date();
		this.todos.forEach(todo => {
			if (todo.dueDate && !todo.completed) {
				const dueDate = new Date(todo.dueDate);
				const timeDiff = dueDate - now;
				const hoursLeft = timeDiff / (1000 * 60 * 60);

				if (hoursLeft > 0 && hoursLeft <= 24) {
					this.showNotification(
						`"${todo.content}" 마감까지 ${Math.ceil(hoursLeft)}시간 남았습니다!`
					);
				}
			}
		});
	}

	async handleSubmit(e) {
		e.preventDefault();
		const title = this.titleInput.value.trim();
		const content = this.contentInput.value.trim();
		const dueDate = this.dueDate.value;

		/**
		if (title) {
			const todo = {
				id: Date.now(),
				title,
				content,
				completed: false,
				createdAt: new Date().toISOString(),
				dueDate: dueDate || null
			};

			this.todos.push(todo);
			this.saveTodos();
			this.renderTodos();
			this.form.reset();
		}
		*/
		if (title) {
			const todo = {
				title,
				content,
				completed: false,
				dueDate: dueDate || null
			};

			try {
				const response = await fetch(this.API_URL, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(todo)
				});
				const newTodo = await response.json();
				this.todos.push(newTodo);
				this.renderTodos();
				this.form.reset();
				this.showNotification('할 일이 추가되었습니다.', 'success');
			} catch (error) {
				this.showNotification('할 일 추가에 실패했습니다.', 'error');
			}
		}
	}

	async toggleTodo(id) {
		/**
		const todo = this.todos.find(todo => todo.id === id);
		if (todo) {
			todo.completed = !todo.completed;
			this.saveTodos();
			this.renderTodos();
		}
		*/
		try {
			const todo = this.todos.find(todo => todo._id === id);
			const response = await fetch(`${this.API_URL}/${id}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ completed: !todo.completed })
			});
			const updatedTodo = await response.json();
			this.todos = this.todos.map(todo =>
				todo._id === id ? updatedTodo : todo
			);
			this.renderTodos();
		} catch (error) {
			this.showNotification('상태 변경에 실패했습니다.', 'error');
			console.error('할 일 완료 상태 변경 중 오류 발생:', error);
		}
	}

	async deleteTodo(id) {
		/**
		if (confirm('정말 삭제하시겠습니까?')) {
			this.todos = this.todos.filter(todo => todo.id !== id);
			this.saveTodos();
			this.renderTodos();
		}
		*/
		if (confirm('정말 삭제하시겠습니까?')) {
			try {
				await fetch(`${this.API_URL}/${id}`, {
					method: 'DELETE'
				});
				this.todos = this.todos.filter(todo => todo._id !== id);
				this.renderTodos();
				this.showNotification('할 일이 삭제되었습니다.', 'success');
			} catch (error) {
				this.showNotification('삭제에 실패했습니다.', 'error');
			}
		}
	}

	editTodo(id) {
		const todoItem = document.querySelector(`[data-id="${id}"]`);
		const todo = this.todos.find(todo => todo._id === id);
		if (!todoItem || !todo) return;

		// 이미 수정 중인 다른 항목이 있다면 취소
		const editingItem = document.querySelector('.todo-item.editing');
		if (editingItem && editingItem !== todoItem) {
			this.cancelEdit(editingItem.dataset.id);
		}

		todoItem.classList.add('editing');
	}

	async saveEdit(id) {
		const todoItem = document.querySelector(`[data-id="${id}"]`);
		if (!todoItem) return;

		const titleInput = todoItem.querySelector('.edit-title');
		const contentInput = todoItem.querySelector('.edit-content');
		const newTitle = titleInput.value.trim();
		const newContent = contentInput.value.trim();

		/**
		if (newTitle) {
			const todo = this.todos.find(todo => todo.id === id);
			if (todo) {
				todo.title = newTitle;
				todo.content = newContent;
				this.saveTodos();
				this.renderTodos();
			}
		}
		*/
		if (newTitle) {
			try {
				const response = await fetch(`${this.API_URL}/${id}`, {
					method: 'PUT',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						title: newTitle,
						content: newContent
					})
				});
				const updatedTodo = await response.json();
				this.todos = this.todos.map(todo =>
					todo._id === id ? updatedTodo : todo
				);
				this.renderTodos();
				this.showNotification('수정이 완료되었습니다.', 'success');
			} catch (error) {
				this.showNotification('수정에 실패했습니다.', 'error');
				console.log(error);
			}
		}
	}

	// cancelEdit 메서드 추가
	cancelEdit(id) {
		const todoItem = document.querySelector(`[data-id="${id}"]`);
		if (todoItem) {
			todoItem.classList.remove('editing');
		}
	}

	toggleDescription(element) {
		//const description = element.nextElementSibling;
		const description = element.previousElementSibling; // 버튼 위치 변경으로 인한 수정
		description.classList.toggle('collapsed');
		element.textContent = description.classList.contains('collapsed') ? '더 보기' : '접기';
	}

	saveTodos() {
		//localStorage.setItem('todos', JSON.stringify(this.todos));
		// localStorage 저장 대신 API 호출로 변경
		// 개별 todo 항목이 이미 서버에 저장되어 있으므로 이 메서드는 제거하거나 필요한 경우에만 사용
	}

	// API 호출을 위한 새로운 메서드들
	// 할 일 목록 불러오기
	async loadTodos() {
		try {
			const response = await fetch(this.API_URL);
			this.todos = await response.json();
			this.renderTodos();
		} catch (error) {
			this.showNotification('할 일 목록을 불러오는데 실패했습니다.', 'error');
		}
	}

	renderTodos() {
		let filteredTodos = [...this.todos];

		// 상태 필터링
		const status = this.statusFilter.value;
		if (status !== 'all') {
			filteredTodos = filteredTodos.filter(todo =>
				status === 'completed' ? todo.completed : !todo.completed
			);
		}

		// 검색
		const searchTerm = this.searchInput.value.toLowerCase();
		if (searchTerm) {
			filteredTodos = filteredTodos.filter(todo =>
				todo.content.toLowerCase().includes(searchTerm)
			);
		}

		// 정렬
		const sortBy = this.sortOption.value;
		filteredTodos.sort((a, b) => {
			if (sortBy === 'due-date' && a.dueDate && b.dueDate) {
				return new Date(a.dueDate) - new Date(b.dueDate);
			}
			return new Date(b.createdAt) - new Date(a.createdAt);
		});

		// renderTodos 메서드 수정 (id 참조를 _id로 변경)
		// todo.id를 todo._id로 변경 ...
		this.todoList.innerHTML = filteredTodos.map(todo => `
			<li class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo._id}">
				<div class="todo-main-content drag-handle">
					<!-- 일반 보기 모드 -->
					<div class="todo-item-content">

						<!-- <input type="checkbox" ${todo.completed ? 'checked' : ''} onchange="todoApp.toggleTodo(${todo._id})"> -->
						<div class="todo-title" ondblclick="todoApp.editTodo('${todo._id}')">${todo.title}</div>
						${todo.content ? `
							<div class="todo-description collapsed" data-content="${todo.content}">${todo.content}</div>
							<button class="toggle-description" style="display: none;" onclick="todoApp.toggleDescription(this)">더 보기</button>
						` : ''}
						${todo.dueDate ? `<span class="due-date">마감: ${todo.dueDate}</span>` : ''}
					</div>

					<!-- 수정 모드 -->
					<div class="edit-form">
						<input type="text" class="edit-title" value="${todo.title}">
						<textarea class="edit-content">${todo.content || ''}</textarea>
						<div class="edit-buttons">
							<button class="save-btn" onclick="todoApp.saveEdit('${todo._id}')">저장</button>
							<button class="cancel-btn" onclick="todoApp.cancelEdit('${todo._id}')">취소</button>
						</div>
					</div>

					<!-- 체크박스를 버튼으로 변경 -->
					<div class="todo-actions">
						<button class="complete-btn ${todo.completed ? 'completed' : ''}" onclick="todoApp.toggleTodo('${todo._id}')">${todo.completed ? '✓' : ''}완료</button>
						<button class="delete-btn" onclick="todoApp.deleteTodo('${todo._id}')">삭제</button>
						<button class="edit-btn" onclick="todoApp.editTodo('${todo._id}')">수정</button>
					</div>
				</div>
			</li>
		`).join('');

		// 렌더링 후 각 설명의 줄 수를 확인하고 더보기 버튼 표시 여부 결정
		this.todoList.querySelectorAll('.todo-description').forEach(desc => {
			if (desc.scrollHeight > desc.clientHeight) {
				const toggleBtn = desc.parentElement.querySelector('.toggle-description');
				if (toggleBtn) {
					toggleBtn.style.display = 'block';
				}
			}
		});
    }
}

const todoApp = new TodoApp();