# Portainer Tools

[**Portainer Tools**](https://google.com) é uma caixa de ferramentas para auxialiar no DevOps de aplicações em docker que utiliza o portainer. <br/>
com esta ferramenta é possivel utilizar o portainer via command line


## 🎨 Funcionalidades
> Principais serviços disponiveis no sistema:
- Atualização da Imagem e Redeploy do Container


## 💻 Pré-requisitos

> Antes de começar, verifique se você atendeu aos seguintes requisitos:

* `python` versão `3.8` ou superior.
* Sistema Operacional `Linux`.
* `.env` com as configurações
* Ler o guia `Como usá-lo`.


## ✨ Como usá-lo

> Baixe o código 
```bash
$ git clone https://github.com/ViniciusCruzMoura/portainer_autodeploy.git
$ cd portainer_autodeploy
```

> Instalar as dependências via `VENV`
```bash
$ bash install.sh
$ source .venv/bin/activate
```

> Configure as variaveis de ambiente `.env`
```bash
$ cat .env #preencha o login, senha e o host
```

> Iniciar a aplicação
```bash
$ python portainer.py help
$ python portainer.py list
$ python portainer.py status STACK_NAME
$ python portainer.py update STACK_NAME
$ python portainer.py prune
```


## 📫 Contribuindo com o Projeto
> Para contribuir com o projeto, siga estas etapas:

1. Clone o projeto: `git clone <url>`
2. Crie uma branch: `git checkout -b <nome_branch>`
3. Faça suas alterações e adicione-as: `git add <nome_arquivo>`
4. Confirme suas alterações: `git commit -m '<mensagem_commit>'`
5. Envie para a branch: `git push origin <nome_branch>`
6. Crie a solicitação de merge

Como alternativa, consulte a documentação do GitLab em [como criar uma solicitação de merge](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html).

<br/>
