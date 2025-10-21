from brevettiai.datamodel.tag import Tag
from brevettiai.platform import PlatformAPI, test_backend


def main():
    # Initialize the PlatformAPI client
    client = PlatformAPI(host=test_backend)

    datasets = client.get_dataset()
    ds = datasets[0]
    
    ## Add tags
    tags = client.get_tag()
    tag = next(Tag.find(tags, "name", "blue"))
    ds.tags.append(tag)
    ds.tags = list({x.id: x for x in ds.tags}.values())
    client.update(ds)

    info = client.get_userinfo()
    permission_group = next(
        x for x in client.get_persmission_groups() if x.name == "My group"
    )

    # Set permissions on the dataset
    permissions = client.get_dataset_permissions(ds)
    client.update_dataset_permission(ds.id, None, permission_group.id, "Editor")
    print(permissions)


if __name__ == "__main__":
    main()
