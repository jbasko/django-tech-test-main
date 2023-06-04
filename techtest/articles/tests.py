import json

from django.test import TestCase
from django.urls import reverse

from techtest.articles.models import Article, Author
from techtest.regions.models import Region


class ArticleListViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("articles-list")
        self.author_1 = Author.objects.create(first_name="John", last_name="Doe")
        self.article_1 = Article.objects.create(title="Fake Article 1")
        self.region_1 = Region.objects.create(code="AL", name="Albania")
        self.region_2 = Region.objects.create(code="UK", name="United Kingdom")
        self.article_2 = Article.objects.create(
            title="Fake Article 2", content="Lorem Ipsum"
        )
        self.article_2.regions.set([self.region_1, self.region_2])

    def test_serializes_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "id": self.article_1.id,
                    "title": "Fake Article 1",
                    "content": "",
                    "regions": [],
                    "author": None,
                },
                {
                    "id": self.article_2.id,
                    "title": "Fake Article 2",
                    "content": "Lorem Ipsum",
                    "regions": [
                        {
                            "id": self.region_1.id,
                            "code": "AL",
                            "name": "Albania",
                        },
                        {
                            "id": self.region_2.id,
                            "code": "UK",
                            "name": "United Kingdom",
                        },
                    ],
                    "author": None,
                },
            ],
        )

    def test_creates_new_article_with_regions(self):
        payload = {
            "title": "Fake Article 3",
            "content": "To be or not to be",
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"code": "AU", "name": "Austria"},
            ],
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 3",
                "content": "To be or not to be",
                "regions": [
                    {
                        "id": regions.all()[0].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                    {"id": regions.all()[1].id, "code": "AU", "name": "Austria"},
                ],
                "author": None,
            },
            response.json(),
        )

    def test_manages_article_with_author(self):
        payload = {
            "title": "Fake Article 4",
            "content": "This is real",
            "regions": [],
            "author": {"id": self.author_1.id},
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        article = Article.objects.last()
        self.assertEqual(article.author.id, self.author_1.id)

        response = self.client.get(
            reverse("article", kwargs={"article_id": article.id}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 4",
                "content": "This is real",
                "regions": [],
                "author": {
                    "id": self.author_1.id,
                    "first_name": "John",
                    "last_name": "Doe",
                },
            },
            response.json(),
        )

        response = self.client.put(
            reverse("article", kwargs={"article_id": article.id}),
            data=json.dumps({
                "title": "Fake Article 4",
                "content": "This is real",
                "regions": [],
                "author": None,
            }),
        )
        self.assertEqual(response.status_code, 200)

        article = Article.objects.last()
        self.assertIsNone(article.author)

        response = self.client.get(
            reverse("article", kwargs={"article_id": article.id}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 4",
                "content": "This is real",
                "regions": [],
                "author": None,
            },
            response.json(),
        )


class ArticleViewTestCase(TestCase):
    def setUp(self):
        self.article = Article.objects.create(title="Fake Article 1")
        self.region_1 = Region.objects.create(code="AL", name="Albania")
        self.region_2 = Region.objects.create(code="UK", name="United Kingdom")
        self.article.regions.set([self.region_1, self.region_2])
        self.url = reverse("article", kwargs={"article_id": self.article.id})

    def test_serializes_single_record_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": self.article.id,
                "title": "Fake Article 1",
                "content": "",
                "regions": [
                    {
                        "id": self.region_1.id,
                        "code": "AL",
                        "name": "Albania",
                    },
                    {
                        "id": self.region_2.id,
                        "code": "UK",
                        "name": "United Kingdom",
                    },
                ],
                "author": None,
            },
        )

    def test_updates_article_and_regions(self):
        # Change regions
        payload = {
            "title": "Fake Article 1 (Modified)",
            "content": "To be or not to be here",
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"id": self.region_2.id},
            ],
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.first()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertEqual(Article.objects.count(), 1)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "regions": [
                    {
                        "id": self.region_2.id,
                        "code": "UK",
                        "name": "United Kingdom",
                    },
                    {
                        "id": regions.all()[1].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                ],
                "author": None,
            },
            response.json(),
        )
        # Remove regions
        payload["regions"] = []
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 0)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "regions": [],
                "author": None,
            },
            response.json(),
        )

    def test_removes_article(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.count(), 0)


class AuthorViewTestCase(TestCase):
    def test_creates_retrieves_updates_and_deletes_author(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }
        response = self.client.post(reverse("authors-list"), data=json.dumps(payload),  content_type="application/json")
        self.assertEqual(response.status_code, 201)

        author = response.json()

        response = self.client.get(reverse("author", kwargs={"author_id": author["id"]}))
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(author, response.json())

        response = self.client.put(
            reverse("author", kwargs={"author_id": author["id"]}),
            data=json.dumps({"first_name": "Jane"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("author", kwargs={"author_id": author["id"]}))
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual({
            "id": author["id"],
            "first_name": "Jane",
            "last_name": "Doe",
        }, response.json())

        response = self.client.get(reverse("authors-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        response = self.client.delete(reverse("author", kwargs={"author_id": author["id"]}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("author", kwargs={"author_id": author["id"]}))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse("authors-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)
