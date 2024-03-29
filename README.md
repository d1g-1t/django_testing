Данный проект представляет собой набор тестов **Unittest** и **Pytest** для **Django**.

**Тесты на unittest для проекта YaNote**
**В файле test_routes.py:**
- главная страница доступна анонимному пользователю.
- аутентифицированному пользователю доступна страница со списком заметок notes/, страница успешного добавления заметки done/, страница добавления новой заметки add/.
- страницы отдельной заметки, удаления и редактирования заметки доступны только автору заметки. Если на эти страницы попытается зайти другой пользователь — вернётся ошибка 404.
- при попытке перейти на страницу списка заметок, страницу успешного добавления записи, страницу добавления заметки, отдельной заметки, редактирования или удаления заметки анонимный пользователь перенаправляется на страницу логина.
- Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны всем пользователям.
**В файле test_content.py:**
- отдельная заметка передаётся на страницу со списком заметок в списке object_list в словаре context;
- в список заметок одного пользователя не попадают заметки другого пользователя;
- на страницы создания и редактирования заметки передаются формы.
**В файле test_logic.py:**
- залогиненный пользователь может создать заметку, а анонимный — не может.
- невозможно создать две заметки с одинаковым slug.
- если при создании заметки не заполнен slug, то он формируется автоматически, с помощью функции pytils.translit.slugify.
- пользователь может редактировать и удалять свои заметки, но не может редактировать или удалять чужие.
**Тесты на pytest для проекта YaNews.**
**В файле test_routes.py:**
- главная страница доступна анонимному пользователю.
- страница отдельной новости доступна анонимному пользователю.
- страницы удаления и редактирования комментария доступны автору комментария.
- при попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
- авторизованный пользователь не может зайти на страницы редактирования или удаления чужих комментариев (возвращается ошибка 404).
- страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.
**В файле test_content.py:**
- количество новостей на главной странице — не более 10.
- новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
- комментарии на странице отдельной новости отсортированы в хронологическом порядке: старые в начале списка, новые — в конце.
- анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости, а авторизованному доступна.
**В файле test_logic.py:**
- анонимный пользователь не может отправить комментарий.
- авторизованный пользователь может отправить комментарий.
- если комментарий содержит запрещённые слова, он не будет опубликован, а форма вернёт ошибку.
- авторизованный пользователь может редактировать или удалять свои комментарии.
- авторизованный пользователь не может редактировать или удалять чужие комментарии.