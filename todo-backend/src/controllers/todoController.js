const Todo = require('../models/todoModel');

// 모든 Todo 가져오기
exports.getAllTodos = async (req, res) => {
  try {
    const todos = await Todo.find().sort({ order: 1 });
    res.json(todos);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Todo 생성
exports.createTodo = async (req, res) => {
  try {
    const maxOrder = await Todo.findOne().sort('-order');
    const order = maxOrder ? maxOrder.order + 1 : 0;

    const todo = new Todo({
      ...req.body,
      order
    });

    const newTodo = await todo.save();
    res.status(201).json(newTodo);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
};

// Todo 업데이트
exports.updateTodo = async (req, res) => {
  try {
    const todo = await Todo.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );

    if (!todo) {
      return res.status(404).json({ message: '할 일을 찾을 수 없습니다.' });
    }

    res.json(todo);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
};

// Todo 삭제
exports.deleteTodo = async (req, res) => {
  try {
    const todo = await Todo.findByIdAndDelete(req.params.id);

    if (!todo) {
      return res.status(404).json({ message: '할 일을 찾을 수 없습니다.' });
    }

    res.json({ message: '삭제되었습니다.' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Todo 순서 업데이트
exports.updateOrder = async (req, res) => {
  try {
    const { todos } = req.body;

    for (let todo of todos) {
      await Todo.findByIdAndUpdate(todo.id, { order: todo.order });
    }

    res.json({ message: '순서가 업데이트되었습니다.' });
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
};