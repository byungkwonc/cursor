# Todo 앱 백엔드 API

## 설치 및 실행 방법

### mongodb 설치 및 실행

```bash
# mongodb 설치 (맥OS 기준)
brew install mongodb-community

# mongodb 서비스 시작
brew services start mongodb/brew/mongodb-community

# 또는 백그라운드 실행 없이 직접 실행
# /opt/homebrew/bin/mongod --> /opt/homebrew/Cellar/mongodb-community/8.0.1/bin/mongod
# /opt/homebrew/etc/mongod.conf
mongod --config /opt/homebrew/etc/mongod.conf

# mongodb 쉘 실행
# /opt/homebrew/bin/mongosh --> /opt/homebrew/Cellar/mongosh/2.3.3/bin/mongosh
# /opt/homebrew/Cellar/mongosh/2.3.3/libexec/lib/node_modules/@mongosh/cli-repl/bin/mongosh.js
mongosh

# MongoDB 상태 확인
brew services list
# 또는
ps aux | grep mongod
# MongoDB 포트 확인
lsof -i tcp:27017
```

### 프로젝트 설정

```bash
# 패키지 설치
npm install

# 서버 실행
npm run dev
```

## 기능

- Todo CRUD 작업
- 순서 관리
- MongoDB를 사용한 데이터 영구 저장
- CORS 지원
- 에러 처리

## 프론트엔드와 연동

- 기존 로컬 스토리지 로직을 API 호출로 교체

```javascript
class TodoApp {
    constructor() {
    this.API_URL = 'http://localhost:3000/api/todos';
    this.todos = []; // 빈 배열로 초기화
    this.initializeElements();
    this.addEventListeners();
    this.initializeSortable();
    this.loadTodos().then(() => {  // loadTodos 완료 후 // localStorage.getItem 대신 API 호출
        this.checkDueDates();
        setInterval(() => this.checkDueDates(), 60000);
    });
    }

 // API 호출을 위한 새로운 메서드들
    async loadTodos() {
        try {
            const response = await fetch(this.API_URL);
            this.todos = await response.json();
            this.renderTodos();
        } catch (error) {
            this.showNotification('할 일 목록을 불러오는데 실패했습니다.', 'error');
        }
    }

    async saveTodos() {
        // localStorage 저장 대신 API 호출로 변경
        // 개별 todo 항목이 이미 서버에 저장되어 있으므로 이 메서드는 제거하거나 필요한 경우에만 사용
    }

    async handleSubmit(e) {
        e.preventDefault();
        const title = this.titleInput.value.trim();
        const content = this.contentInput.value.trim();
        const dueDate = this.dueDate.value;

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
        try {
            const todo = this.todos.find(todo => todo._id === id);
            const response = await fetch(`${this.API_URL}/${id}`, {
                method: 'PATCH',
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
        }
    }

    async deleteTodo(id) {
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

    async saveEdit(id) {
        const todoItem = document.querySelector(`[data-id="${id}"]`);
        if (!todoItem) return;

        const titleInput = todoItem.querySelector('.edit-title');
        const contentInput = todoItem.querySelector('.edit-content');
        const newTitle = titleInput.value.trim();
        const newContent = contentInput.value.trim();

        if (newTitle) {
            try {
                const response = await fetch(`${this.API_URL}/${id}`, {
                    method: 'PATCH',
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
            }
        }
    }

    // renderTodos 메서드 수정 (id 참조를 _id로 변경)
    renderTodos() {
        // ... 기존 필터링 및 정렬 로직 ...

        this.todoList.innerHTML = filteredTodos.map(todo => `
            <li class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo._id}">
                // ... 나머지 HTML 템플릿은 동일하되 todo.id를 todo._id로 변경 ...
            </li>
        `).join('');

        // ... 나머지 렌더링 로직 ...
    }
}
```
